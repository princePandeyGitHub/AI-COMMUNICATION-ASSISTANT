# AI-Communication-Assistant
AI-Powered Email Support Assistant – Automates customer support workflows by fetching emails from Gmail, filtering &amp; prioritizing queries, analyzing sentiment, generating AI-driven replies, and visualizing insights on an interactive Streamlit dashboard.


Demonstration video--- https://youtu.be/BYJXmMMh_0k?si=ZhIWU3u1-Phprj8f


<h1>Documentation</h1>

Now days organizations receives thousands of email daily so, it requires a lot of manual effort to
filter support-related emails and requests and working with these emails requires a lot of time and energy.<br>
--Here comes our solution <h3>Ai-Communication-Assistant</h3> aimed to improve efficiency, response quality,
and customer satisfaction while reducing manual effort.

<h2>Features: </h2>
1.Email fetching: Uses Gmail API to retrieve recent emails.<br>
2.Data Cleaning: Extracts clean text from plain or HTML messages.<br>
3.Keyword Filtering: Seperates support-related queries.<br>
4.Priority Detection: Identifies urgent emails.<br>
5.Sentiment Analysis: Classifies customer tone(positive/negative/neutral).<br>
6.AI reply Generation: Drafts professional email responses.<br>
7.Information extraction: Important information such as contact details, customer requirements, any metadata is extracted.<br>

<h2>Architecture: </h2>
1.Fetch Emails(Gmail API 0auth) -- fetches emails and saves them to fetched_emails.csv file.<br>
2.Preprocessing(clean text) -- Extracts clean text from email for better processing.<br>
3.Keyword Filter(Non-relevant emails ignored) -- Emails with keywords(support,query,help,request) are stored in dataframe.<br>
4.Priority Check(urgent/not urgent) -- Priority(urgent/not urgent) is assigned to each email and urgent emails are shifted
above for early processing.<br>
5.Sentimental Analysis(twitter-roberta-base-sentiment) -- A sentiment(positive/negative/neutral) is assigned to each email.<br>
6.AI Model(llama-3.1-8b-instant) -- Replies are generated and added along with email with extracted information.<br>
7.-- After all these emails are saved with these properties to processed_emails.csv file.<br>
8.Dashboard -- processed emails are loaded and present to a simple and clean streamlit dashboard for visualization & Insights.<br>

<h2>Approach Used: </h2>
1. Fetch_email.py -- In order to fetch emails we first created a Gmail API, after that we gets our credentials.json file to 
be used in this script. We defines a scope after that , in this particular case it's mentioned as read only. After successfully
executing the script it will open a page in browser for authorization, right now only testing accounts are allowed and i had
set my only one gmail account , authorization will be done after that with two clicks. Now token.json file will be created in
the same folder this file will be crucial since i will not need to authorize again and again locally.Now we will get the desired
number of recent emails and after that we will get values(sender,subject,body,sent_date) and after cleaning the body will save these
emails to fetched_emails.csv file.<br>

2.sample_emails.csv -- Since these are personal emails and they will not have keywords(support,help,query,requests e.t.c.) i will
use sample emails that were provided and will do everything with sample emails not with actual emails but doing it with real
emails is also similar we just will be need to load fetched_emails.csv instead of sample_emails.csv in our processing.py script.<br>

3.processing.py -- We processes the emails in following steps :<br>
3.1. Firstly loads the sample emails and creates and dataframe filtered_emails with same columns as sample emails.<br>
3.2. I creates a list after that with specific keywords and matches with sample emails if there's a match i simply append them<br>
to filtered emails dataframe , this way all the filtered emails are extracted and now processing will be done with this dataframe.<br>
3.3. Similarly we creates a list of priority keywords and matches with each filtered email and urgent/not urgent is assigned to new 
column priority and after that we arranges these emails so that urgent ones are placed above.<br>
3.4. Now each email is passed to twitter-roberta-base-sentiment model to get the sentiment associated with it and gets assigned
to a new column sentiment<br>
3.5. Similarly each email is passed to llama-3.1-8b-instant model for reply generation and information extraction and in the same
way these are also assigned to new columns suggested_reply and information respectively.<br>
3.6. At the end filtered_emails.csv that now have columns such as sender, subject, body, date, priority, sentiment, suggested_reply,
important_information is saved to file processed_emails.csv in the same folder.<br>
3.7. Now, the processing have been completed and processed emails have also been saved as a csv file.<br>

4.dashboard.py -- We generates the streamlit dashboard in following steps:<br>
4.1. Firstly loads the processed emails csv file for the dashboard generation.<br>
4.2. Side bar filters -- Four filters are provided in the side bar such as filter for senders(different senders), priority(urgent
/not urgent), sentiment(positive/negative/neutral), date range filter.<br>
4.3. Charts -- Following charts are shown to the dashboard:<br>
			4.3.1. A Line chart is used to represent number of emails received with time(dates).<br>
			4.3.2. A pie chart is used to represent the distribution between urgent and non-urgent emails.<br>
			4.3.2. Bar charts are used to show the frequency of emails sent by sender and frequency of emails with different sentiments<br>
			4.3.3. Wordcloud is used to show the mostly used words<br>
4.4. Email explorer -- A drop down have been provided to selected between different emails and in this urgent emails will apper
at top and a particular email can be selected and few things like sender,contact details, subject, email body along with a 
suggested reply that can be reviewed and edited will be provide along with a approve reply button for now it's a dummy button.<br>
4.5. Raw data -- processed emails is also provided at the bottom<br>


<h2>How to use this: </h2>
1.Install dependencies : pip install -r requiremetns.txt<br>
2.Google API credentials : place your credentials.json in the project root and run the script fetch_emails.py to generate token.js<br>
3.Configure API key : create a .env file in the project root with API_KEY = 'your_api_key'<br>
4.Run the pipeline: <br>
	4.1. python fetch_emails.py - fetches emails from Gmail<br>
	4.2. python processing.py - processes & analyzes them<br>
	4.3. streamlit run dashboard.py - launcehs the dashboard<br>



<h2>Developed by: </h2>
<h3>Prince Pandey</h3>






