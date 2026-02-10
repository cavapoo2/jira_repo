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

    def build_table(self, headers, rows):
        """
        Build a Jira wiki markup table

        Args:
            headers: List of column header strings
                     e.g. ["Name", "Status", "Notes"]
            rows: List of row lists
                     e.g. [["Item 1", "Done", "All good"],
                            ["Item 2", "In Progress", "Ongoing"]]

        Returns:
            Formatted wiki markup table string
        """
        # Build header row  - || denotes a header cell in wiki markup
        header_row = "|| " + " || ".join(headers) + " ||"

        # Build data rows - | denotes a regular cell in wiki markup
        data_rows = []
        for row in rows:
            # Pad row with empty strings if fewer cells than headers
            padded_row = row + [""] * (len(headers) - len(row))
            data_rows.append("| " + " | ".join(str(cell) for cell in padded_row) + " |")

        # Join everything together
        table = "\n".join([header_row] + data_rows)
        return table

    def build_description(self, sections):
        """
        Build a full description with multiple sections, text, and tables.

        Args:
            sections: List of dicts, each with a 'type' key:
                - {'type': 'heading', 'text': 'My Heading'}
                - {'type': 'text', 'text': 'Some paragraph text'}
                - {'type': 'table', 'headers': [...], 'rows': [[...]]}
                - {'type': 'divider'}

        Returns:
            Full formatted description string
        """
        parts = []

        for section in sections:
            section_type = section.get('type')

            if section_type == 'heading':
                # h2. is a heading in wiki markup
                parts.append(f"h2. {section['text']}")

            elif section_type == 'subheading':
                parts.append(f"h3. {section['text']}")

            elif section_type == 'text':
                parts.append(section['text'])

            elif section_type == 'table':
                table = self.build_table(
                    section['headers'],
                    section['rows']
                )
                parts.append(table)

            elif section_type == 'divider':
                parts.append("----")  # Horizontal rule in wiki markup

        return "\n\n".join(parts)

    def create_story(self, project_key, summary, description="", **kwargs):
        """
        Create a Jira story with optional fields

        Args:
            project_key: Project key (e.g., 'PROJ')
            summary: Story summary/title
            description: Story description (plain text or wiki markup)
            **kwargs: Optional fields like priority, labels, assignee
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
                print(f"  URL: {self.jira_url}/browse/{result.get('key')}")
                return result
            else:
                print(f"✗ Failed: {response.status_code}")
                print(f"  Error: {response.text}")
                return None

        except Exception as e:
            print(f"✗ Error: {e}")
            return None


# ── Example usage ─────────────────────────────────────────────────────────────

if __name__ == "__main__":

    creator = JiraStoryCreator(
        jira_url="https://your-server:8443",
        pat_token="your-personal-access-token",
        cert_path="/path/to/certificate.pem"
    )

    if creator.test_connection():

        # Build a description with headings, text, and tables
        description = creator.build_description([
            {
                'type': 'heading',
                'text': 'Overview'
            },
            {
                'type': 'text',
                'text': 'This story covers the implementation of the user authentication module.'
            },
            {
                'type': 'heading',
                'text': 'Acceptance Criteria'
            },
            {
                'type': 'table',
                'headers': ['#', 'Criteria', 'Priority', 'Status'],
                'rows': [
                    ['1', 'User can log in with email and password', 'High',   'To Do'],
                    ['2', 'User sees error on invalid credentials',  'High',   'To Do'],
                    ['3', 'Session expires after 30 minutes',        'Medium', 'To Do'],
                    ['4', 'Password reset via email link',           'Medium', 'To Do'],
                ]
            },
            {
                'type': 'divider'
            },
            {
                'type': 'heading',
                'text': 'Technical Notes'
            },
            {
                'type': 'table',
                'headers': ['Component', 'Technology', 'Notes'],
                'rows': [
                    ['Auth Service', 'OAuth 2.0',    'Use existing SSO provider'],
                    ['Database',     'PostgreSQL',   'Users table already exists'],
                    ['Frontend',     'React',        'Use AuthContext hook'],
                ]
            },
        ])

        # Create the story
        creator.create_story(
            project_key="PROJ",
            summary="Implement user authentication module",
            description=description,
            priority="High",
            labels=["backend", "security"]
        )
```

## What the Table Looks Like in Jira

The wiki markup renders like this in Jira:
```
|| #  || Criteria                              || Priority || Status ||
| 1   | User can log in with email and password | High      | To Do  |
| 2   | User sees error on invalid credentials  | High      | To Do  |
| 3   | Session expires after 30 minutes        | Medium    | To Do  |
