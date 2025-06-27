import os
from github import Github
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GITHUB_PAT = os.getenv("GITHUB_PAT")

from datetime import datetime, timezone

def fetch_github_activity(username: str, start_date: str, end_date: str) -> List[Dict]:
    g = Github(os.getenv("GITHUB_PAT"))
    user = g.get_user(username)
    repos = user.get_repos()

    # Ensure datetime objects are timezone-aware in UTC
    start_dt = datetime.fromisoformat(start_date).replace(tzinfo=timezone.utc)
    end_dt = datetime.fromisoformat(end_date).replace(tzinfo=timezone.utc)

    activity = []

    for repo in repos:
        # Compare UTC-aware datetimes
        if repo.created_at < start_dt and repo.pushed_at < start_dt:
            continue

        try:
            commits = list(repo.get_commits(since=start_dt, until=end_dt))  # Force evaluate
        except Exception as e:
            print(f"Error fetching commits for {repo.name}: {e}")
            continue

        if not commits:
            print(f"No commits found for {repo.name} in range {start_date} to {end_date}")
            continue  # Skip repos with no commits

        commit_messages = []
        for c in commits[:5]:
            try:
                msg = c.commit.message.strip()
                commit_messages.append(msg)
            except Exception as e:
                commit_messages.append("⚠️ Commit message unavailable")

        try:
            readme = repo.get_readme().decoded_content.decode("utf-8")
        except:
            readme = "No README available."

        activity.append({
    "repo": repo.name,
    "url": repo.html_url,  # ✅ Add repo link here
    "description": repo.description or "No description provided.",
    "readme": readme[:400] + "..." if len(readme) > 400 else readme
})



    return activity
