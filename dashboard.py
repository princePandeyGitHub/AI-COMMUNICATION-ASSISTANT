import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv("processed_emails.csv")
    df['sent_date'] = pd.to_datetime(df['sent_date'], errors='coerce')
    return df

df = load_data()

st.set_page_config(page_title="Customer Support Dashboard", layout="wide")

# Sidebar Filters
st.sidebar.header("🔍 Filters")
senders = st.sidebar.multiselect("Filter by Sender", df['sender'].unique())
priorities = st.sidebar.multiselect("Filter by Priority", df['priority'].unique())

# FIXED sentiment list
all_sentiments = ["negative", "neutral", "positive"]
sentiments = st.sidebar.multiselect("Filter by Sentiment", all_sentiments, default=all_sentiments)

date_range = st.sidebar.date_input("Date Range", [df['sent_date'].min(), df['sent_date'].max()])

# Apply Filters
filtered_df = df.copy()
if senders:
    filtered_df = filtered_df[filtered_df['sender'].isin(senders)]
if priorities:
    filtered_df = filtered_df[filtered_df['priority'].isin(priorities)]
if sentiments:
    filtered_df = filtered_df[filtered_df['sentiment'].isin(sentiments)]
filtered_df = filtered_df[
    (filtered_df['sent_date'].dt.date >= date_range[0]) &
    (filtered_df['sent_date'].dt.date <= date_range[1])
]

# Layout
st.title("📧 Customer Support Dashboard")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Emails", len(filtered_df))
col2.metric("Urgent Emails", filtered_df[filtered_df['priority']=="urgent"].shape[0])
col3.metric("Negative", filtered_df[filtered_df['sentiment']=="negative"].shape[0])
col4.metric("Neutral", filtered_df[filtered_df['sentiment']=="neutral"].shape[0])
col5.metric("Positive", filtered_df[filtered_df['sentiment']=="positive"].shape[0])

# Charts
st.subheader("📊 Email Trends & Insights")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Trends", "⚡ Priority", "😊 Sentiment", "👥 Senders", "📝 Issues"])

with tab1:
    emails_over_time = filtered_df.groupby(filtered_df['sent_date'].dt.date).size().reset_index(name="count")
    fig = px.line(emails_over_time, x="sent_date", y="count", title="Emails Over Time")
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    fig = px.pie(filtered_df, names="priority", title="Priority Distribution")
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    sentiment_count = (
    filtered_df['sentiment']
    .value_counts()
    .reindex(all_sentiments, fill_value=0)   # ensures all 3 sentiments exist
    .reset_index()
    )
    sentiment_count.columns = ['sentiment', 'count']
    fig = px.bar(sentiment_count, x="sentiment", y="count", title="Sentiment Breakdown", labels={'sentiment':'Sentiment','count':'Count'})
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    sender_count = filtered_df['sender'].value_counts().reset_index()
    fig = px.bar(sender_count, x="sender", y="count", title="Top Senders", labels={'sender':'Sender','count':'Count'})
    st.plotly_chart(fig, use_container_width=True)

with tab5:
    text = " ".join(filtered_df['important_information'].dropna().astype(str))
    if text.strip():
        wordcloud = WordCloud(width=800, height=400, background_color="white").generate(text)
        fig, ax = plt.subplots(figsize=(10,5))
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig)
    else:
        st.info("No issue keywords available for this selection.")

# Email Explorer
st.subheader("📂 Email Explorer")
selected_email = st.selectbox("Select an email to view details", filtered_df['subject'])

if selected_email:
    email_row = filtered_df[filtered_df['subject'] == selected_email].iloc[0]

    st.markdown(f"""
    ### ✉️ {email_row['subject']}
    **From:** {email_row['sender']}  
    **Date:** {email_row['sent_date']}  
    **Priority:** {email_row['priority']}  
    **Sentiment:** {email_row['sentiment']}  

    **📌 Email Body:**  
    {email_row['body']}  
    """)

    # Editable Suggested Reply
    st.markdown("### 💡 Suggested Reply (Review & Edit)")
    edited_reply = st.text_area(
        "Edit before approving:",
        email_row['suggested_reply'],
        height=200,
        key=f"reply_{email_row['subject']}"
    )

    # Dummy Approve Button
    if st.button("✅ Approve Reply"):
        st.success("Reply approved ✅ (not actually sent, dummy action)")

    # Important Information
    st.markdown("---")
    st.markdown("### 📑 Important Information")
    st.write(email_row['important_information'])

# Raw Data
with st.expander("📄 View Raw Data"):
    st.dataframe(filtered_df)
