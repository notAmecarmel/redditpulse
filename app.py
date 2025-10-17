import streamlit as st
import praw
import google.generativeai as genai
import os

# Configure API keys
REDDIT_CLIENT_ID = st.secrets["reddit"]["client_id"]
REDDIT_CLIENT_SECRET = st.secrets["reddit"]["client_secret"]
REDDIT_USER_AGENT = st.secrets["reddit"]["user_agent"]

USER_AGENT = os.getenv("USER_AGENT") or st.secrets["USER_AGENT"]
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or st.secrets["GEMINI_API_KEY"]

# Initialize Reddit
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=USER_AGENT
)

# Initialize Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# --- Fetch Reddit posts ---
def fetch_top_posts(subreddit_name, limit=10):
    try:
        subreddit = reddit.subreddit(subreddit_name)
        posts = []
        for post in subreddit.hot(limit=limit):
            text = post.selftext if post.selftext else post.title
            posts.append(text)
        return posts
    except Exception as e:
        return [f"Error fetching subreddit: {e}"]

# --- Summarize posts with Gemini ---
def summarize_posts(posts):
    joined_text = "\n\n".join(posts)
    prompt = f"""
    You are an analyst AI. Summarize the following Reddit posts. 
    Highlight the main discussion themes, community sentiment (positive/negative/neutral), 
    and any repeated opinions or emerging trends. 
    Output in 3 short sections: Summary, Sentiment Overview, and Key Takeaways.

    Posts:
    {joined_text[:8000]}  # limit to avoid overload
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating summary: {e}"

# --- Streamlit UI ---
st.set_page_config(page_title="RedditPulse AI", page_icon="📊")
st.title("📊 RedditPulse AI — Trend & Sentiment Summarizer")
st.write("Get instant AI summaries of trending Reddit discussions.")

subreddit = st.text_input("Enter subreddit name (e.g. stocks, startups, india):")
limit = st.slider("Number of posts to analyze:", 5, 30, 10)

if st.button("Analyze"):
    with st.spinner("Fetching data..."):
        posts = fetch_top_posts(subreddit, limit)
    with st.spinner("Analyzing sentiment..."):
        summary = summarize_posts(posts)
    st.subheader("🔍 Summary & Insights")
    st.write(summary)
