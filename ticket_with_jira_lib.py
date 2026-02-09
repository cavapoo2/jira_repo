from jira import JIRA
import json

# Connect to Jira
jira = JIRA(
    server='https://your-domain.atlassian.net',
    basic_auth=('your-email@example.com', 'your-api-token')
)

def create_stories_with_library(json_file_path):
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    
    issues = data if isinstance(data, list) else [data]
    
    for issue_data in issues:
        fields = {
            'project': {'key': issue_data['project_key']},
            'summary': issue_data['summary'],
            'description': issue_data.get('description', ''),
            'issuetype': {'name': 'Story'},
        }
        
        # Add optional fields
        if 'priority' in issue_data:
            fields['priority'] = {'name': issue_data['priority']}
        if 'labels' in issue_data:
            fields['labels'] = issue_data['labels']
        
        new_issue = jira.create_issue(fields=fields)
        print(f"Created: {new_issue.key}")

# Install with: pip install jira
create_stories_with_library('jira_tickets.json')
