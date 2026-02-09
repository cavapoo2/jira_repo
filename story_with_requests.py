import requests
import json

# Configuration
JIRA_URL = "https://your-server:8443"
PAT_TOKEN = "your-personal-access-token"
CERT_PATH = "/path/to/certificate.pem"

# Headers
HEADERS = {
    "Authorization": f"Bearer {PAT_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def create_story(project_key, summary, description=""):
    """
    Create a Jira story ticket
    """
    endpoint = f"{JIRA_URL}/rest/api/2/issue"
    
    payload = {
        "fields": {
            "project": {
                "key": project_key
            },
            "summary": summary,
            "description": description,
            "issuetype": {
                "name": "Story"
            }
        }
    }
    
    try:
        response = requests.post(
            endpoint,
            headers=HEADERS,
            data=json.dumps(payload),
            verify=CERT_PATH,
            timeout=10
        )
        
        if response.status_code == 201:
            result = response.json()
            issue_key = result.get('key')
            print(f"✓ Story created successfully!")
            print(f"  Issue Key: {issue_key}")
            print(f"  Issue ID: {result.get('id')}")
            print(f"  URL: {JIRA_URL}/browse/{issue_key}")
            return result
        else:
            print(f"✗ Failed to create story")
            print(f"  Status Code: {response.status_code}")
            print(f"  Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def get_projects():
    """
    List all available projects
    """
    endpoint = f"{JIRA_URL}/rest/api/2/project"
    
    try:
        response = requests.get(
            endpoint,
            headers=HEADERS,
            verify=CERT_PATH,
            timeout=10
        )
        
        if response.status_code == 200:
            projects = response.json()
            print(f"✓ Found {len(projects)} projects:")
            for project in projects:
                print(f"  - {project['key']}: {project['name']}")
            return projects
        else:
            print(f"✗ Failed to get projects: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return None


# Example usage
if __name__ == "__main__":
    # First, get available projects
    print("=== Available Projects ===")
    get_projects()
    
    print("\n=== Creating Story ===")
    # Create a story
    create_story(
        project_key="PROJ",  # Replace with your project key
        summary="Build user authentication system",
        description="Implement OAuth 2.0 with Google and GitHub providers"
    )
