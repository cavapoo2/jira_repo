from jira import JIRA

# Connect
jira = JIRA(
    server="https://your-server:8443",
    token_auth="your-personal-access-token",
    options={'verify': '/path/to/certificate.pem', 'async': False},
    timeout=10
)

# Create a simple story
def create_story():
    story_fields = {
        'project': {'key': 'PROJ'},  # Replace with your project key
        'summary': 'Build user login page',
        'description': 'Create a responsive login page with email and password fields',
        'issuetype': {'name': 'Story'},
    }
    
    try:
        new_story = jira.create_issue(fields=story_fields)
        print(f"✓ Story created successfully!")
        print(f"  Issue Key: {new_story.key}")
        print(f"  URL: {jira.server}/browse/{new_story.key}")
        return new_story
    except Exception as e:
        print(f"✗ Failed to create story: {e}")
        return None

if __name__ == "__main__":
    create_story()
