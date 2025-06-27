import subprocess
import textwrap

def call_ollama(prompt: str, model: str = "mistral") -> str:
    """Calls the local Ollama model with a prompt and returns the response."""
    try:
        result = subprocess.run(
            ["ollama", "run", model, prompt],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"❌ Ollama Error: {e.stderr.strip()}"

def generate_post_with_ollama(spotlight_projects: list, summary: list, start_date: str, end_date: str) -> str:
    spotlight_text = ""
    support_text = ""

    for item in summary:
        block = f"""
Project: {item['repo']}
Description: {item['readme']}
Link: {item['url']}
"""
        if item['repo'] in spotlight_projects:
            spotlight_text += block
        else:
            support_text += block

    print("🔦 Spotlight Projects:", spotlight_projects)
    print("⭐ Spotlight Text:\n", spotlight_text)
    print("📦 Support Text:\n", support_text)

    # Sample posts for tone/reference
    examples = textwrap.dedent("""
    🧩 Puzzle mode on 🧩
    Just wrapped up building a real-time sentiment analysis app using RoBERTa and computer vision – it's exciting to see words and expressions come together for a deeper emotional understanding. Also worked on a portfolio analyzer that helps visualize asset allocation and prediction trends!
    github.com/myprofile/emotion-analyzer
    github.com/myprofile/portfolio-dashboard
    Grateful for the creative stretch this brought. #buildinpublic #AIprojects #studentdeveloper

    🔍 From Scan to Insight 🔍
    Trained a fine-tuned OCR model to handle tricky form layouts and noisy data, leading to 40% fewer errors in our test dataset. Also revamped a client’s admin portal using React + AWS – clean, fast, and way more usable now.
    github.com/myprofile/ocr-trainer
    github.com/myprofile/react-admin-revamp
    One step closer to making AI more accessible. #machinelearning #reactjs #womenintech

    🎯 Weekend well spent 🎯
    Just finished working on a personalized care plan generator using local LLMs and natural language understanding. It’s built for caregivers and families to get structured plans from plain descriptions.
    github.com/myprofile/caresketch
    Small projects, big impact. #hackathon #llm #socialgood
    """)

    # Final prompt to Ollama
    prompt = textwrap.dedent(f"""
    You are helping create a professional yet warm LinkedIn post summarizing recent GitHub activity.
    You are me and draft a post talking about what you have been up to between {start_date} and {end_date}.

    Here are a few examples of how I usually write my posts. Match this tone and structure:

    {examples}

    🧠 Guidelines:
    - Begin with one emoji, a short catchy post title in plain text, and the same emoji again.
    - Highlight **Spotlight Projects** using short, natural summaries (not full descriptions), use:
    {spotlight_text}
    - Mention the other projects briefly in an **Other Projects** section, use:
    {support_text}
    - Summaries should be 1 line per project, no bullets unless necessary.
    - Include GitHub links as plain text.
    - Use human, proud, humble tone. Don’t sound like a bot.
    - End with a light motivational sentence and relevant hashtags.
    """)

    return call_ollama(prompt)
