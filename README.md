# 📝 GitHub → LinkedIn Post Generator (Local LLM Powered)

Turn your GitHub activity into a polished LinkedIn post — with just one click.

## 🔍 Overview

This tool summarizes your recent GitHub activity into a LinkedIn-style post using a local LLM (via [Ollama](https://ollama.com)). It emphasizes your spotlight projects while also briefly mentioning other contributions. It’s perfect for developers who want to share progress without spending time crafting every word.

## ✨ Features

- 🧠 Generates human-like LinkedIn posts based on your commits and READMEs  
- 🔦 Highlights spotlight projects in more detail  
- 📦 Summarizes other projects under an "Other Projects" section  
- 📅 Allows custom date range selection for your activity  
- 📚 Uses sample post references to match your personal tone  
- ⚡ Powered by your locally running Ollama model (e.g., Mistral)

## 📦 Tech Stack

- Python 3
- Ollama (for local LLM inference)
- GitHub API or preprocessed GitHub data
- `subprocess` for command-line calls to Ollama

## 🚀 Getting Started

1. **Install [Ollama](https://ollama.com) and pull a model:**
    ```bash
    ollama pull mistral
    ```

2. **Clone this repo and install dependencies (if any):**
    ```bash
    git clone https://github.com/synamalhan/git-post
    cd github-linkedin-generator
    ```

3. **Run the script with your GitHub data:**
    ```python
    python main.py
    ```
    *(Note: You can integrate this with a Streamlit UI or automate GitHub activity fetching.)*

## 🧠 Prompt Strategy

The tool constructs a prompt including:

* Sample posts for tone
* A summary of spotlight projects with descriptions + commits
* Other projects in short
* Natural language instruction to keep the tone proud but not robotic

The final prompt is passed to Ollama via CLI for generation.

## 🛠 Sample Prompt Format

```
🧩 Puzzle mode on 🧩  
Just wrapped up building a real-time sentiment analysis app using RoBERTa and computer vision...  
github.com/yourprofile/emotion-analyzer  
Small projects, big impact. #AI #buildinpublic #weekendbuild
```

## 📁 File Structure

```
.
├── main.py                  # Core script with prompt generation
├── github_utils.py         # (Optional) Helper to fetch GitHub activity
├── ollama_generator.py     # Ollama call and prompt logic
├── sample_output.md        # Example post outputs
└── README.md               # You’re here
```

## 🤖 Model Used

Currently uses `mistral` via Ollama CLI. You can easily change it to `llama3`, `gemma`, or any model you’ve pulled.

## 📌 Notes

* This tool assumes preprocessed GitHub activity (commits + READMEs + repo info).
* To avoid page refreshes in web UI, debounce interaction or manage session state carefully.

## ✅ Example Output

> 🎯 Weekend well spent 🎯  
> Just finished working on a personalized care plan generator using local LLMs...  
> github.com/myprofile/caresketch  
> One step at a time. #hackathon #llm #socialimpact

## 📄 License

MIT License. Free to use and customize.
