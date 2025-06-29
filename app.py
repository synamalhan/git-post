import streamlit as st
import os
from datetime import datetime, timedelta
from github_utils import fetch_github_activity
from ollama_generator import generate_post_with_ollama, call_ollama
import traceback

# Page configuration
st.set_page_config(
    page_title="GitHub LinkedIn Post Generator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 1rem 1rem;
    }
    .stButton > button {
        width: 100%;
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    .project-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
    }
    .spotlight-card {
        background: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
        margin: 0.5rem 0;
    }
    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
    .chat-message {
        background: #e3f2fd;
        padding: 0.75rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 3px solid #2196f3;
    }
    .ai-response {
        background: #f3e5f5;
        padding: 0.75rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 3px solid #9c27b0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🚀 GitHub LinkedIn Post Generator</h1>
    <p>Transform your GitHub activity into engaging LinkedIn posts</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'github_data' not in st.session_state:
    st.session_state.github_data = None
if 'generated_post' not in st.session_state:
    st.session_state.generated_post = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'spotlight_projects' not in st.session_state:
    st.session_state.spotlight_projects = []

# Sidebar for instructions
with st.sidebar:
    st.markdown("### 📋 Instructions")
    st.markdown("""
    1. **Setup**: Make sure you have Ollama installed and running locally
    2. **GitHub Token**: Create a `.env` file with your GitHub Personal Access Token
    3. **Date Range**: Select a meaningful period (e.g., last month)
    4. **Projects**: Choose 2-3 spotlight projects for maximum impact
    5. **Generate**: Let AI create your professional LinkedIn post
    6. **Refine**: Chat with AI to improve your post
    """)
    
    st.markdown("### 🔧 Requirements")
    st.markdown("""
    - Ollama running locally
    - GitHub PAT in `.env` file
    - Internet connection for GitHub API
    """)

# Main interface
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 📊 GitHub Activity Input")
    
    # Input form
    with st.form("github_form"):
        username = st.text_input(
            "GitHub Username",
            placeholder="Enter your GitHub username",
            help="Your GitHub username (without @)"
        )
        
        col_start, col_end = st.columns(2)
        with col_start:
            start_date = st.date_input(
                "Start Date",
                value=datetime.now() - timedelta(days=30),
                help="Beginning of the activity period"
            )
        
        with col_end:
            end_date = st.date_input(
                "End Date",
                value=datetime.now(),
                help="End of the activity period"
            )
        
        submit_button = st.form_submit_button("🔍 Fetch GitHub Activity")
    
    # Fetch GitHub data
    if submit_button:
        if not username:
            st.error("Please enter a GitHub username")
        elif start_date >= end_date:
            st.error("Start date must be before end date")
        else:
            with st.spinner("Fetching GitHub activity..."):
                try:
                    github_data = fetch_github_activity(username, start_date, end_date)
                    if github_data:
                        st.session_state.github_data = github_data
                        st.session_state.generated_post = None  # Reset post when new data is fetched
                        st.session_state.chat_history = []  # Reset chat history
                        st.success(f"Found {len(github_data)} repositories with activity!")
                    else:
                        st.warning("No repositories found with activity in the specified date range")
                except Exception as e:
                    st.error(f"Error fetching GitHub data: {str(e)}")
                    st.error("Make sure your GitHub PAT is set in the .env file")

with col2:
    st.markdown("### 🎯 Project Selection & Post Generation")
    
    if st.session_state.github_data:
        # Project selection
        repo_options = []
        for item in st.session_state.github_data:
            repo = item['repo']
            commits_count = len(item['commits'])
            repo_display = f"**{repo}** ({commits_count} commits)"
            repo_options.append((repo_display, repo))
        
        spotlight_projects = st.multiselect(
            "🌟 Select Spotlight Projects (2-3 recommended)",
            options=[option[0] for option in repo_options],
            help="These will be featured prominently in your LinkedIn post"
        )
        
        # Convert display names back to repo names
        spotlight_repo_names = []
        for display_name in spotlight_projects:
            for display, repo_name in repo_options:
                if display == display_name:
                    spotlight_repo_names.append(repo_name)
                    break
        
        st.session_state.spotlight_projects = spotlight_repo_names
        
        # Generate post button
        if st.button("🤖 Generate LinkedIn Post", disabled=len(spotlight_repo_names) == 0):
            if not spotlight_repo_names:
                st.error("Please select at least one spotlight project")
            else:
                with st.spinner("Generating LinkedIn post with AI..."):
                    try:
                        # Prepare data for LLM
                        spotlight_data = []
                        other_data = []
                        
                        for item in st.session_state.github_data:
                            if item['repo'] in spotlight_repo_names:
                                spotlight_data.append(item)
                            else:
                                other_data.append(item)
                        
                        # Generate the post
                        generated_post = generate_post_with_ollama(
                            spotlight_data, 
                            other_data, 
                            start_date, 
                            end_date
                        )
                        
                        if generated_post:
                            st.session_state.generated_post = generated_post
                            st.session_state.chat_history = []  # Reset chat history for new post
                            st.markdown("""
                            <div class="success-message">
                                ✅ LinkedIn post generated successfully!
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.error("Failed to generate post. Make sure Ollama is running.")
                    
                    except Exception as e:
                        st.error(f"Error generating post: {str(e)}")
                        st.error("Make sure Ollama is installed and running locally")

# Project Details Section
if st.session_state.github_data:
    st.markdown("---")
    st.markdown("### 📂 Project Details")
    
    # Separate projects into spotlight and non-spotlight
    spotlight_data = []
    other_data = []
    
    for item in st.session_state.github_data:
        if item['repo'] in st.session_state.spotlight_projects:
            spotlight_data.append(item)
        else:
            other_data.append(item)
    
    col_spotlight, col_other = st.columns([1, 1])
    
    with col_spotlight:
        with st.expander(f"🌟 Spotlight Projects ({len(spotlight_data)})", expanded=True):
            if spotlight_data:
                for item in spotlight_data:
                    st.markdown(f"""
                    <div class="spotlight-card">
                        <h4>{item['repo']}</h4>
                        <p><strong>Description:</strong> {item.get('description', 'No description')}</p>
                        <p><strong>Language:</strong> {item.get('language', 'Not specified')}</p>
                        <p><strong>Stars:</strong> {item.get('stars', 0)} ⭐</p>
                        <p><strong>Commits:</strong> {len(item['commits'])}</p>
                        <p><strong>Recent commits:</strong></p>
                        <ul>
                    """, unsafe_allow_html=True)
                    
                    for commit in item['commits'][:3]:
                        st.markdown(f"<li>{commit}</li>", unsafe_allow_html=True)
                    
                    st.markdown(f"""
                        </ul>
                        <p><strong>URL:</strong> <a href="{item['url']}" target="_blank">{item['url']}</a></p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No spotlight projects selected")
    
    with col_other:
        with st.expander(f"📁 Other Projects ({len(other_data)})", expanded=False):
            if other_data:
                for item in other_data:
                    st.markdown(f"""
                    <div class="project-card">
                        <h4>{item['repo']}</h4>
                        <p><strong>Description:</strong> {item.get('description', 'No description')}</p>
                        <p><strong>Language:</strong> {item.get('language', 'Not specified')}</p>
                        <p><strong>Stars:</strong> {item.get('stars', 0)} ⭐</p>
                        <p><strong>Commits:</strong> {len(item['commits'])}</p>
                        <p><strong>URL:</strong> <a href="{item['url']}" target="_blank">{item['url']}</a></p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("All projects are in spotlight")

# Generated post display and chat interface
if st.session_state.generated_post:
    st.markdown("---")
    st.markdown("### 📝 Generated LinkedIn Post")
    
    col_post, col_chat = st.columns([2, 1])
    
    with col_post:
        st.text_area(
            "Your LinkedIn Post",
            st.session_state.generated_post,
            height=300,
            help="Copy this content to your LinkedIn post"
        )
        
        # Post metrics
        char_count = len(st.session_state.generated_post)
        st.metric("Character Count", char_count)
        
        if char_count > 3000:
            st.warning("⚠️ Post is quite long. Consider shortening for better engagement.")
        elif char_count > 1300:
            st.success("✅ Good length for LinkedIn!")
        else:
            st.info("ℹ️ Post is on the shorter side")
    
    with col_chat:
        st.markdown("#### 💬 Chat with AI")
        st.markdown("Refine your post by chatting with the AI")
        
        # Chat input
        user_message = st.text_input(
            "Ask for changes:",
            placeholder="e.g., Make it more casual, add more emojis, shorten it...",
            key="chat_input"
        )
        
        if st.button("💬 Send Message") and user_message:
            # Add user message to chat history
            st.session_state.chat_history.append({"role": "user", "content": user_message})
            
            with st.spinner("AI is thinking..."):
                try:
                    # Create a prompt for refining the post
                    refine_prompt = f"""You are helping refine a LinkedIn post. Here's the current post:

{st.session_state.generated_post}

The user wants this change: {user_message}

Please provide the updated LinkedIn post that incorporates their feedback. Return ONLY the updated post, no explanations or additional text."""
                    
                    # Get AI response
                    ai_response = call_ollama(refine_prompt)
                    
                    if ai_response:
                        # Update the generated post
                        st.session_state.generated_post = ai_response.strip()
                        # Add AI response to chat history
                        st.session_state.chat_history.append({"role": "ai", "content": "Post updated successfully!"})
                        st.rerun()
                    else:
                        st.error("Failed to get AI response")
                        
                except Exception as e:
                    st.error(f"Error communicating with AI: {str(e)}")
        
        # Display chat history
        if st.session_state.chat_history:
            st.markdown("#### 💭 Chat History")
            for i, message in enumerate(st.session_state.chat_history[-5:]):  # Show last 5 messages
                if message["role"] == "user":
                    st.markdown(f"""
                    <div class="chat-message">
                        <strong>You:</strong> {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="ai-response">
                        <strong>AI:</strong> {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
        
        # Clear chat button
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()
        
        # Regenerate button
        if st.button("🔄 Regenerate Post"):
            st.session_state.generated_post = None
            st.session_state.chat_history = []
            st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem 0;">
    Built with ❤️ using Streamlit | Powered by Ollama | 
    <a href="https://github.com" target="_blank">GitHub API</a>
</div>
""", unsafe_allow_html=True)