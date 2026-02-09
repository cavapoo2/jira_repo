from jira import JIRA

# Configuration
JIRA_URL = "https://your-server:8443"
PAT_TOKEN = "your-personal-access-token"
CERT_PATH = "/path/to/your/certificate.pem"

# Connect using PAT
jira = JIRA(
    server=JIRA_URL,
    token_auth=PAT_TOKEN,  # Use token_auth instead of basic_auth
    options={
        'verify': CERT_PATH,  # Path to your certificate
        'async': False
    },
    timeout=10
)

# Test connection
try:
    current_user = jira.current_user()
    print(f"✓ Connected as: {current_user}")
    
    # List projects
    projects = jira.projects()
    print(f"\n✓ Available projects:")
    for project in projects:
        print(f"  - {project.key}: {project.name}")
    
except Exception as e:
    print(f"✗ Error: {e}")
