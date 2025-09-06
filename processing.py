import os
from dotenv import load_dotenv
import pandas as pd
from transformers import pipeline
import requests

# function to add new rows to the data frame
def add_new_row(sender, subject, body, date, data_frame):
    data_frame.loc[len(data_frame)] = {
        "sender": sender,
        "subject": subject,
        "body": body,
        "sent_date": date
    }
    return data_frame

# function to check whether the keywords exists in particular email subject
def checkMatch(subject, keywords):
    for keyword in keywords:
        if subject.find(keyword) != -1:
            return True
    return False

# selecting model for sentimental analysis
sentiment_analyzer = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment")

# function to perform sentiment analysis
def analyze_sentiment(text):
    result = sentiment_analyzer(text[:512])[0]  # truncate long emails
    return result["label"]

# API setup
load_dotenv()  # load variables from .env
API_KEY = os.getenv("API_KEY")
API_URL = "https://api.groq.com/openai/v1/chat/completions"

# NEW function: Generate reply + extract information in one API call
def generate_reply_and_extract(email_body, email_sender, email_subject, email_date):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": (
                "You are a professional email assistant.\n"
                "For the given email, do two tasks:\n"
                "1. Draft a polite, concise reply.\n"
                "2. Extract key information in this format:\n"
                "---Information---\n"
                "Contact details: ...\n"
                "Customer requirements: ...\n"
                "Sentiment: ...\n"
                "Metadata: ...\n"
            )},
            {"role": "user", "content": f"Sender: {email_sender}\nSubject: {email_subject}\nDate: {email_date}\nEmail: {email_body}"}
        ],
        "max_tokens": 400,
        "temperature": 0.7
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    data = response.json()

    if "choices" not in data:
        return {"reply": f"API Error: {data}", "info": ""}

    content = data["choices"][0]["message"]["content"]

    # simple parsing: split at ---Information---
    if "---Information---" in content:
        reply_part, info_part = content.split("---Information---", 1)
    else:
        reply_part, info_part = content, ""

    return {"reply": reply_part.strip(), "info": info_part.strip()}

def main():
    # Read dataset (it's the actual emails we got)
    emails = pd.read_csv("./sample_emails.csv")

    # it will contain filtered emails
    filtered_emails = pd.DataFrame(columns=emails.columns)

    # these are the keyword from which we will search
    keywords = ["support", "query", "request", "help"]

    # iterate over each email
    for i in range(len(emails)):
        subject = emails.iloc[i]['subject']

        # search whether this particular email subject contains keywords or not
        isMatched = checkMatch(subject.lower(), keywords)

        # if it contains keywords simply append them to filtered_emails
        if isMatched:
            add_new_row(
                emails.iloc[i]['sender'],
                emails.iloc[i]['subject'],
                emails.iloc[i]['body'],
                emails.iloc[i]['sent_date'],
                filtered_emails
            )

    # priority words
    priority_keywords = ["immediately", "critical", "cannot access", "urgent", "immediate"]

    # iterate over every filtered email
    for i in range(len(filtered_emails)):
        subject = filtered_emails.iloc[i]['subject']

        # check whether contain priority words or not
        isMatched = checkMatch(subject.lower(), priority_keywords)

        # if yes add new priority with value urgent else not urgent
        if isMatched:
            filtered_emails.at[i, 'priority'] = 'urgent'
        else:
            filtered_emails.at[i, 'priority'] = 'not urgent'

    # now sort the emails so urgent ones appear first
    filtered_emails = filtered_emails.sort_values(
        by="priority",
        ascending=True,
        key=lambda col: col.map({"urgent": 0, "not urgent": 1})
    ).reset_index(drop=True)

    # Assign sentiment + AI reply + info
    for i in range(len(filtered_emails)):
        # perform sentiment analysis
        sentiment_label = analyze_sentiment(filtered_emails.at[i,'body'])

        if sentiment_label == "LABEL_0":
            filtered_emails.at[i,'sentiment'] = "negative"
        elif sentiment_label == "LABEL_1":
            filtered_emails.at[i,'sentiment'] = "neutral"
        else:
            filtered_emails.at[i,'sentiment'] = 'positive'

        # AI reply + info (single API call)
        email_body = filtered_emails.at[i, 'body']
        email_sender = filtered_emails.at[i, 'sender']
        email_subject = filtered_emails.at[i, 'subject']
        email_date = filtered_emails.at[i, 'sent_date']

        try:
            result = generate_reply_and_extract(email_body, email_sender, email_subject, email_date)
            filtered_emails.at[i, 'suggested_reply'] = result['reply']
            filtered_emails.at[i, 'important_information'] = result['info']
        except Exception as e:
            filtered_emails.at[i, 'suggested_reply'] = f"Error: {e}"
            filtered_emails.at[i, 'important_information'] = f"Error: {e}"

    # save processed emails
    filtered_emails.to_csv("processed_emails.csv", index=False)

if __name__ == "__main__":
    main()
