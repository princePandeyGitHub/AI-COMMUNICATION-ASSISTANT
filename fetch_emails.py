from __future__ import print_function
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
import base64
import re
import csv

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_clean_email_text(msg):
    payload = msg['payload']

    def decode_data(data):
        return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')

    text = ""

    # Single part
    if 'body' in payload and 'data' in payload['body']:
        text = decode_data(payload['body']['data'])

    # Multipart
    elif 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                text = decode_data(part['body']['data'])
                break
        else:
            # fallback to HTML if no plain text
            for part in payload['parts']:
                if part['mimeType'] == 'text/html' and 'data' in part['body']:
                    html = decode_data(part['body']['data'])
                    text = BeautifulSoup(html, "html.parser").get_text()
                    break

    # Clean zero-width chars and normalize spaces
    text = re.sub(r'[\u200b\u200c\u200d\uFEFF]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def main():
    count = 0

    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    results = service.users().messages().list(userId='me', maxResults=5).execute()
    messages = results.get('messages', [])

    if not messages:
        print('No messages found.')
        return

    # Prepare CSV file: overwrite each time, add headers
    with open("fetched_emails.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["sender", "subject", "body", "sent_date"])

        for m in messages:
            msg = service.users().messages().get(userId='me', id=m['id'], format='full').execute()
            headers = {h['name']: h['value'] for h in msg.get('payload', {}).get('headers', [])}

            body = get_clean_email_text(msg)

            # Extract fields for CSV
            sender = headers.get("From", "")
            subject = headers.get("Subject", "")
            date = headers.get("Date", "")
            body_csv = body.replace("\n", " ").replace(",", " ")

            writer.writerow([sender, subject, body_csv, date])

            count += 1

    print(f"{count} emails saved to emails.csv")


if __name__ == '__main__':
    main()
