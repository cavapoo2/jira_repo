import requests
import json

class JiraStoryCreator:
    def __init__(self, jira_url, pat_token, cert_path):
        self.jira_url = jira_url
        self.headers = {
            "Authorization": f"Bearer {pat_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        self.cert_path = cert_path
    
    def test_connection(self):
        """Test connection to Jira"""
        try:
            response = requests.get(
                f"{self.jira_url}/rest/api/2/myself",
                headers=self.headers,
                verify=self.cert_path,
                timeout=5
            )
            if response.status_code == 200:
                user = response.json()
                print(f"✓ Connected as: {user.get('displayName')}")
                return True
            else:
                print(f"✗ Connection failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Connection error: {e}")
            return False
    
    def create_story(self, project_key, summary, description="", **kwargs):
        """
        Create a Jira story with optional fields
        
        Args:
            project_key: Project key (e.g., 'PROJ')
            summary: Story summary/title
            description: Story description
            **kwargs: Optional fields like priority, labels, assignee, etc.
        """
        endpoint = f"{self.jira_url}/rest/api/2/issue"
        
        payload = {
            "fields": {
                "project": {"key": project_key},
                "summary": summary,
                "description": description,
                "issuetype": {"name": "Story"}
            }
        }
        
        # Add optional fields
        if "priority" in kwargs:
            payload["fields"]["priority"] = {"name": kwargs["priority"]}
        
        if "labels" in kwargs:
            payload["fields"]["labels"] = kwargs["labels"]
        
        if "assignee" in kwargs:
            payload["fields"]["assignee"] = {"name": kwargs["assignee"]}
        
        try:
            response = requests.post(
                endpoint,
                headers=self.headers,
                data=json.dumps(payload),
                verify=self.cert_path,
                timeout=10
            )
            
            if response.status_code == 201:
                result = response.json()
                print(f"✓ Story created: {result.get('key')}")
                return result
            else:
                print(f"✗ Failed: {response.status_code}")
                print(f"  Error: {response.text}")
                return None
                
        except Exception as e:
            print(f"✗ Error: {e}")
            return None


# Usage
if __name__ == "__main__":
    creator = JiraStoryCreator(
        jira_url="https://your-server:8443",
        pat_token="your-personal-access-token",
        cert_path="/path/to/certificate.pem"
    )
    
    # Test connection
    if creator.test_connection():
        # Create story
        creator.create_story(
            project_key="PROJ",
            summary="Implement user dashboard",
            description="Create a responsive dashboard with widgets",
            priority="High",
            labels=["frontend", "ui"]
        )
