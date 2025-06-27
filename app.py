import streamlit as st
from github_utils import fetch_github_activity
from ollama_generator import generate_post_with_ollama
import datetime

st.set_page_config(page_title="GitHub → LinkedIn Post Generator", layout="centered")
st.title("📢 GitHub → LinkedIn Post Generator")

# Initialize session state keys
if "summary" not in st.session_state:
    st.session_state.summary = None

# GitHub Form
with st.form("gh-form"):
    username = st.text_input("GitHub Username", placeholder="e.g. syna-m")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=datetime.date.today().replace(day=1))
    with col2:
        end_date = st.date_input("End Date", value=datetime.date.today())
    submitted = st.form_submit_button("Fetch GitHub Activity")

# On submit, store summary in session state
if submitted:
    with st.spinner("Fetching GitHub activity..."):
        try:
            summary = fetch_github_activity(username, str(start_date), str(end_date))
            if not summary:
                st.warning("No activity found in that date range.")
            else:
                st.success("GitHub activity fetched successfully!")
                st.session_state.summary = summary
        except Exception as e:
            st.error(f"Error: {e}")

# If summary exists, show spotlight selector
if st.session_state.summary:
    summary = st.session_state.summary
    repo_titles = [item['repo'] for item in summary]

    selected = st.multiselect("🔦 Choose Spotlight Projects", repo_titles)
    spotlight_items = [item for item in summary if item['repo'] in selected]
    other_items = [item for item in summary if item['repo'] not in selected]
    st.write(spotlight_items)
    st.write(other_items)

    if st.button("✨ Generate LinkedIn Post"):
        with st.spinner("Generating post with Ollama..."):
            post = generate_post_with_ollama(spotlight_items, summary, str(start_date), str(end_date))
            st.success("Here’s your LinkedIn post:")
            st.text_area("Generated Post", post, height=400)
