import subprocess
import json
import sys
from datetime import datetime
import traceback

def check_ollama_available():
    """Check if Ollama is installed and running"""
    try:
        result = subprocess.run(['ollama', 'list'], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stdout
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return False, str(e)

def get_available_models():
    """Get list of available Ollama models"""
    try:
        result = subprocess.run(['ollama', 'list'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            models = []
            for line in lines:
                if line.strip():
                    model_name = line.split()[0]
                    models.append(model_name)
            return models
        return []
    except Exception:
        return []
    
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

def format_project_data(project_data):
    """Format project data for the LLM prompt"""
    formatted = []
    for item in project_data:
        project_info = f"**{item['repo']}**"
        if item.get('readme'):
            project_info += f" - {item['readme']}"
        
        if item.get('language'):
            project_info += f" (Built with {item['language']})"
        
        if item.get('commits'):
            project_info += f"\nKey commits: {', '.join(item['commits'][:3])}"
        
        project_info += f"\nGitHub: {item['url']}"
        formatted.append(project_info)
    
    return formatted

def create_linkedin_prompt(spotlight_projects, other_projects, start_date, end_date):
    """Create a detailed prompt for the LLM to generate a LinkedIn post"""
    
    # Format dates
    date_range = f"{start_date.strftime('%B %d')} to {end_date.strftime('%B %d, %Y')}"
    
    # Format project data
    spotlight_formatted = format_project_data(spotlight_projects)
    other_formatted = format_project_data(other_projects)
    
    # Create the prompt
    prompt = f"""You are a professional LinkedIn content creator. Generate a human-sounding, engaging LinkedIn post about recent GitHub activity.

CONTEXT:
- Date range: {date_range}
- Spotlight projects: {len(spotlight_projects)} main projects to highlight
- Supporting projects: {len(other_projects)} additional projects to mention briefly, mention all the projects but keep it concise.

SPOTLIGHT PROJECTS:
{chr(10).join(spotlight_formatted)}

OTHER PROJECTS:
{chr(10).join(other_formatted) if other_formatted else "None"}

REQUIREMENTS:
1. Start with an engaging title using ONE emoji at the beginning and end
2. Write in first person with a humble, professional tone
3. Create a "Highlights" or "Spotlight" section for main projects
4. Briefly mention other projects in 1-2 lines each
5. Include actual GitHub links as plain text (not markdown)
6. End with a motivational statement about building/learning
7. Add relevant hashtags (3-5 maximum)
8. Keep total length under 2000 characters
9. Use plain text formatting - NO markdown syntax
10. Make it sound human and authentic, not corporate

TONE EXAMPLES:
- "Just wrapped up an exciting month of coding..."
- "Been busy building some cool projects..."
- "Excited to share what I've been working on..."

STRUCTURE:
[Emoji] [Engaging Title] [Emoji]

[Brief intro paragraph about the period/activity]

✨ Highlights:
- [Project 1 with brief description and link]
- [Project 2 with brief description and link]
- [Project 3 if applicable]

[Brief mention of other projects if any]

[Motivational closing line about learning/building]

[3-5 relevant hashtags]

Generate the LinkedIn post now:"""

    return prompt

def call_ollama_generate(prompt, model='llama3'):
    """Call Ollama to generate text based on the prompt"""
    try:
        # Prepare the command
        cmd = ['ollama', 'run', model, '--prompt', prompt]
        
        # Run Ollama
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            error_msg = result.stderr if result.stderr else "Unknown error"
            raise Exception(f"Ollama error: {error_msg}")
            
    except subprocess.TimeoutExpired:
        raise Exception("Ollama request timed out. The model might be taking too long to respond.")
    except FileNotFoundError:
        raise Exception("Ollama not found. Please install Ollama and make sure it's in your PATH.")
    except Exception as e:
        raise Exception(f"Error calling Ollama: {str(e)}")

def clean_generated_post(raw_output):
    """Clean and format the generated post"""
    # Remove any system messages or artifacts
    lines = raw_output.split('\n')
    cleaned_lines = []
    skip_patterns = ['```', '---', 'Here is', 'Here\'s']
    
    for line in lines:
        line = line.strip()
        if line and not any(pattern in line for pattern in skip_patterns):
            cleaned_lines.append(line)
    
    # Join lines and clean up extra spaces
    cleaned_post = '\n'.join(cleaned_lines)
    
    # Remove excessive line breaks
    while '\n\n\n' in cleaned_post:
        cleaned_post = cleaned_post.replace('\n\n\n', '\n\n')
    
    return cleaned_post.strip()

def generate_post_with_ollama(spotlight_projects, other_projects, start_date, end_date, model='llama3'):
    """
    Main function to generate a LinkedIn post using Ollama
    
    Args:
        spotlight_projects: List of main projects to highlight
        other_projects: List of other projects to mention briefly
        start_date: Start date of the activity period
        end_date: End date of the activity period
        model: Ollama model to use (default: llama3)
    
    Returns:
        Generated LinkedIn post as string
    """
    try:
        print(f"Generating LinkedIn post using model: {model}")
        
        # Check if Ollama is available
        is_available, message = check_ollama_available()
        if not is_available:
            raise Exception(f"Ollama is not available: {message}")
        
        # Get available models
        available_models = get_available_models()
        if model not in available_models:
            if available_models:
                model = available_models[0]  # Use first available model
                print(f"Model '{model}' not found. Using '{model}' instead.")
            else:
                raise Exception("No Ollama models found. Please install a model first (e.g., 'ollama pull llama3')")
        
        # Create the prompt
        prompt = create_linkedin_prompt(spotlight_projects, other_projects, start_date, end_date)
        print("Generated prompt for LLM")
        
        # Generate the post
        print("Calling Ollama to generate post...")
        raw_output = call_ollama(prompt, model)
        
        # Clean and format the output
        cleaned_post = clean_generated_post(raw_output)
        
        print("Successfully generated LinkedIn post")
        return cleaned_post
        
    except Exception as e:
        print(f"Error generating post: {str(e)}")
        print(traceback.format_exc())
        return None

def generate_sample_reference_post():
    """Generate a sample reference post for testing"""
    return """🚀 October Development Wrap-Up 🚀

Just finished an amazing month of coding and shipping new projects! Been diving deep into AI tools and web development.

✨ Highlights:
- TaskFlow: Built a modern task management app with React and TypeScript. Clean UI, drag-and-drop functionality, and local storage. GitHub: https://github.com/username/taskflow
- AI Chat Helper: Created an intelligent chat assistant using OpenAI's API. Features conversation memory and context awareness. GitHub: https://github.com/username/ai-chat-helper
- Portfolio Redesign: Completely rebuilt my portfolio site with Next.js and Tailwind CSS. GitHub: https://github.com/username/portfolio-v3

Also worked on smaller projects: improved my Python automation scripts and contributed to open source documentation.

Always excited about building tools that solve real problems and learning new technologies along the way!

#BuildInPublic #AI #WebDevelopment #React #OpenSource"""

if __name__ == "__main__":
    # Test the module
    print("Testing Ollama integration...")
    
    # Check if Ollama is available
    is_available, message = check_ollama_available()
    print(f"Ollama available: {is_available}")
    if is_available:
        print(f"Available models: {get_available_models()}")
    else:
        print(f"Error: {message}")
        print("\nTo install Ollama:")
        print("1. Visit https://ollama.ai and install Ollama")
        print("2. Run 'ollama pull llama3' to download a model")
        print("3. Make sure Ollama is running")
    
    # Show sample output
    print("\n" + "="*50)
    print("SAMPLE LINKEDIN POST:")
    print("="*50)
    print(generate_sample_reference_post())