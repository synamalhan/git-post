# 🚀 GitHub LinkedIn Post Generator

Transform your GitHub activity into engaging LinkedIn posts using AI! This Streamlit application fetches your recent GitHub repositories and commits, then uses Ollama (local LLM) to generate professional LinkedIn posts.

## ✨ Features

- **GitHub Integration**: Fetches repositories, commits, and README content
- **Smart Date Filtering**: Analyze activity within any date range
- **Project Categorization**: Select spotlight vs supporting projects
- **AI-Powered Generation**: Uses Ollama for human-sounding LinkedIn posts
- **Professional Formatting**: Includes emojis, highlights, links, and hashtags
- **Secure**: Uses environment variables for API tokens

## 🛠️ Setup Instructions

### 1. Prerequisites

- Python 3.8+
- [Ollama](https://ollama.ai) installed and running locally
- GitHub Personal Access Token

### 2. Installation

```bash
# Clone or download the project files
git clone https://github.com/synamalhan/git-post.git
cd github-linkedin-generator

# Install Python dependencies
pip install -r requirements.txt

# Install and setup Ollama
# Visit https://ollama.ai for installation instructions
ollama pull llama3  # or your preferred model
```

### 3. Environment Setup

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your GitHub PAT
# Get your token from: https://github.com/settings/tokens
```

Your `.env` file should look like:
```
GITHUB_PAT=github_pat_11XXXXXXXXXX_your_actual_token_here
OLLAMA_MODEL=llama3
```

### 4. GitHub Personal Access Token

1. Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Select scopes:
   - `public_repo` (for public repositories)
   - `repo` (if you want to include private repositories)
4. Copy the token and add it to your `.env` file

### 5. Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📖 How to Use

1. **Enter GitHub Username**: Your GitHub username (without @)
2. **Select Date Range**: Choose the period you want to analyze
3. **Fetch Activity**: Click to retrieve your GitHub activity
4. **Select Projects**: Choose 2-3 spotlight projects for maximum impact
5. **Generate Post**: Let AI create your professional LinkedIn post
6. **Copy & Share**: Copy the generated post to LinkedIn

## 🔧 Configuration

### Ollama Models

The app uses `llama3` by default, but you can use any installed Ollama model:

```bash
# See available models
ollama list

# Install a different model
ollama pull mistral
ollama pull codellama
```

Update your `.env` file to use a different model:
```
OLLAMA_MODEL=mistral
```

### GitHub API Limits

- **Without token**: 60 requests/hour
- **With token**: 5,000 requests/hour

The app is optimized to minimize API calls, but a token is highly recommended.

## 📋 Project Structure

```
├── app.py                 # Main Streamlit application
├── github_utils.py        # GitHub API integration
├── ollama_generator.py    # LLM post generation
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore           # Git ignore rules
└── README.md           # This file
```

## 🐛 Troubleshooting

### Common Issues

**"Ollama not found"**
- Install Ollama from https://ollama.ai
- Make sure it's in your system PATH
- Verify with: `ollama --version`

**"GITHUB_PAT not found"**
- Check your `.env` file exists and has the correct token
- Verify the token has proper permissions
- Test with: `python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('GITHUB_PAT'))"`

**"No repositories found"**
- Check the date range covers periods with activity
- Verify the GitHub username is correct
- Make sure you have public repositories or token has repo access

**API Rate Limiting**
- Use a GitHub Personal Access Token
- Wait for the rate limit to reset (shown in error message)

### Testing Components

Test GitHub integration:
```bash
python github_utils.py
```

Test Ollama integration:
```bash
python ollama_generator.py
```

## 🎯 Usage Tips

1. **Optimal Date Range**: 2-4 weeks usually provides good content
2. **Project Selection**: Choose 2-3 diverse, interesting projects
3. **Post Length**: Generated posts are optimized for LinkedIn's algorithm
4. **Customization**: Edit the generated post to match your personal style
5. **Hashtags**: The AI includes relevant hashtags, but you can customize them

## 🔒 Security

- Never commit your `.env` file to version control
- Your GitHub token is stored locally and never transmitted
- Ollama runs locally, so your data stays private

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests!

## 📄 License

This project is open source and available under the MIT License.

---

**Happy posting!** 🚀✨