import os
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv
import traceback

# Load environment variables
load_dotenv()

class GitHubAPIError(Exception):
    """Custom exception for GitHub API errors"""
    pass

def get_github_headers():
    """Get headers for GitHub API requests"""
    token = os.getenv('GITHUB_PAT')
    if not token:
        raise GitHubAPIError("GITHUB_PAT not found in environment variables. Please check your .env file.")
    
    return {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'GitHub-LinkedIn-Generator'
    }

def fetch_user_repos(username):
    """Fetch all repositories for a given username"""
    headers = get_github_headers()
    repos = []
    page = 1
    per_page = 100
    
    while True:
        url = f'https://api.github.com/users/{username}/repos'
        params = {
            'per_page': per_page,
            'page': page,
            'sort': 'updated',
            'type': 'all'
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 404:
            raise GitHubAPIError(f"User '{username}' not found on GitHub")
        elif response.status_code == 403:
            raise GitHubAPIError("GitHub API rate limit exceeded or token invalid")
        elif response.status_code != 200:
            raise GitHubAPIError(f"GitHub API error: {response.status_code} - {response.text}")
        
        page_repos = response.json()
        if not page_repos:
            break
            
        repos.extend(page_repos)
        page += 1
        
        # Limit to prevent excessive API calls
        if len(repos) >= 300:
            break
    
    return repos

def fetch_repo_commits(username, repo_name, since_date, until_date):
    """Fetch commits for a repository within date range"""
    headers = get_github_headers()
    commits = []
    page = 1
    per_page = 100
    
    # Convert dates to ISO format
    since_iso = since_date.strftime('%Y-%m-%dT%H:%M:%SZ')
    until_iso = until_date.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    while True:
        url = f'https://api.github.com/repos/{username}/{repo_name}/commits'
        params = {
            'since': since_iso,
            'until': until_iso,
            'per_page': per_page,
            'page': page,
            'author': username  # Only get commits by the user
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 409:
            # Repository is empty
            return []
        elif response.status_code != 200:
            print(f"Warning: Could not fetch commits for {repo_name}: {response.status_code}")
            return []
        
        page_commits = response.json()
        if not page_commits:
            break
            
        commits.extend(page_commits)
        page += 1
        
        # Get top 10 commits maximum
        if len(commits) >= 10:
            break
    
    return commits[:5]  # Return top 5 commits

def fetch_repo_readme(username, repo_name):
    """Fetch README content for a repository"""
    headers = get_github_headers()
    
    # Try different README variations
    readme_files = ['README.md', 'README.rst', 'README.txt', 'README']
    
    for readme_file in readme_files:
        url = f'https://api.github.com/repos/{username}/{repo_name}/contents/{readme_file}'
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            content = response.json()
            if content.get('encoding') == 'base64':
                import base64
                readme_content = base64.b64decode(content['content']).decode('utf-8')
                # Return first 500 characters
                return readme_content[:500] + ("..." if len(readme_content) > 500 else "")
    
    return None

def filter_repos_by_date(repos, since_date, until_date):
    """Filter repositories that have been updated within the date range"""
    filtered_repos = []
    
    # Convert input dates to timezone-aware datetime objects
    if isinstance(since_date, datetime):
        since_dt = since_date.replace(tzinfo=timezone.utc)
    else:
        since_dt = datetime.combine(since_date, datetime.min.time()).replace(tzinfo=timezone.utc)
    
    if isinstance(until_date, datetime):
        until_dt = until_date.replace(tzinfo=timezone.utc)
    else:
        until_dt = datetime.combine(until_date, datetime.max.time()).replace(tzinfo=timezone.utc)
    
    for repo in repos:
        # Parse repository update date
        updated_at = datetime.fromisoformat(repo['updated_at'].replace('Z', '+00:00'))
        
        # Check if repo was updated in the date range
        if since_dt <= updated_at <= until_dt:
            filtered_repos.append(repo)
    
    return filtered_repos

def fetch_github_activity(username, start_date, end_date):
    """
    Main function to fetch GitHub activity for a user within a date range
    
    Returns:
        List of dictionaries with keys: repo, url, description, commits, readme
    """
    try:
        print(f"Fetching GitHub activity for {username} from {start_date} to {end_date}")
        
        # Fetch all user repositories
        all_repos = fetch_user_repos(username)
        print(f"Found {len(all_repos)} total repositories")
        
        # Filter repositories by date range
        filtered_repos = filter_repos_by_date(all_repos, start_date, end_date)
        print(f"Found {len(filtered_repos)} repositories updated in date range")
        
        activity_data = []
        
        for repo in filtered_repos:
            try:
                repo_name = repo['name']
                print(f"Processing repository: {repo_name}")
                
                # Fetch commits for this repository
                commits = fetch_repo_commits(username, repo_name, 
                                           datetime.combine(start_date, datetime.min.time()).replace(tzinfo=timezone.utc),
                                           datetime.combine(end_date, datetime.max.time()).replace(tzinfo=timezone.utc))
                
                # Skip repositories with no commits in the date range
                if not commits:
                    continue
                
                # Fetch README content
                readme_content = fetch_repo_readme(username, repo_name)
                
                # Format commit messages
                commit_messages = []
                for commit in commits:
                    message = commit['commit']['message'].split('\n')[0]  # First line only
                    commit_messages.append(message)
                
                # Create activity data entry
                activity_entry = {
                    'repo': repo_name,
                    'url': repo['html_url'],
                    'description': repo.get('description', ''),
                    'commits': commit_messages,
                    'readme': readme_content,
                    'language': repo.get('language'),
                    'stars': repo.get('stargazers_count', 0),
                    'topics': repo.get('topics', [])
                }
                
                activity_data.append(activity_entry)
                print(f"Added {repo_name} with {len(commit_messages)} commits")
                
            except Exception as e:
                print(f"Error processing repository {repo.get('name', 'unknown')}: {str(e)}")
                continue
        
        print(f"Successfully processed {len(activity_data)} repositories")
        return activity_data
        
    except GitHubAPIError as e:
        raise e
    except Exception as e:
        print(f"Unexpected error in fetch_github_activity: {str(e)}")
        print(traceback.format_exc())
        raise GitHubAPIError(f"Unexpected error: {str(e)}")

def validate_github_token():
    """Validate that the GitHub token is working"""
    try:
        headers = get_github_headers()
        response = requests.get('https://api.github.com/user', headers=headers)
        
        if response.status_code == 200:
            user_data = response.json()
            return True, user_data.get('login', 'Unknown')
        else:
            return False, f"Invalid token: {response.status_code}"
    except Exception as e:
        return False, str(e)

if __name__ == "__main__":
    # Test the module
    from datetime import datetime, timedelta
    
    # Test token validation
    is_valid, result = validate_github_token()
    print(f"Token validation: {is_valid} - {result}")
    
    if is_valid:
        # Test fetching activity
        username = input("Enter GitHub username to test: ")
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        try:
            activity = fetch_github_activity(username, start_date, end_date)
            print(f"\nFound activity for {len(activity)} repositories:")
            for item in activity[:3]:  # Show first 3
                print(f"- {item['repo']}: {len(item['commits'])} commits")
        except Exception as e:
            print(f"Error: {e}")