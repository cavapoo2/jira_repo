import requests
from requests.auth import HTTPBasicAuth

# Test basic connectivity
JIRA_URL = "http://your-server:8080"
USERNAME = "your-username"
PASSWORD = "your-password"

# Simple API call to check connection
try:
    response = requests.get(
        f"{JIRA_URL}/rest/api/2/myself",
        auth=HTTPBasicAuth(USERNAME, PASSWORD),
        timeout=5
    )
    
    if response.status_code == 200:
        print("✓ Connection successful!")
        print(f"Logged in as: {response.json()['displayName']}")
    else:
        print(f"✗ Connection failed: {response.status_code}")
        print(response.text)
        
except requests.exceptions.Timeout:
    print("✗ Connection timeout - server not responding")
except requests.exceptions.ConnectionError as e:
    print(f"✗ Connection error: {e}")
except Exception as e:
    print(f"✗ Error: {e}")
