import requests
import json
import os


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

    def build_table(self, rows, headers=None):
        """
        Build a Jira wiki markup table

        Args:
            rows:    List of row lists
                     e.g. [["Item 1", "Done", "All good"],
                            ["Item 2", "In Progress", "Ongoing"]]
            headers: Optional list of column header strings
                     e.g. ["Name", "Status", "Notes"]

        Returns:
            Formatted wiki markup table string
        """
        table_rows = []

        # Add header row only if headers are provided
        if headers:
            header_row = "|| " + " || ".join(headers) + " ||"
            table_rows.append(header_row)

        # Build data rows
        for row in rows:
            col_count = len(headers) if headers else len(rows[0])
            padded_row = row + [""] * (col_count - len(row))
            table_rows.append("| " + " | ".join(str(cell) for cell in padded_row) + " |")

        return "\n".join(table_rows)

    def build_description(self, sections):
        """
        Build a full description with multiple sections, text, and tables.

        Args:
            sections: List of dicts, each with a 'type' key:
                - {'type': 'heading',    'text': 'My Heading'}
                - {'type': 'subheading', 'text': 'My Subheading'}
                - {'type': 'text',       'text': 'Some paragraph text'}
                - {'type': 'table',      'rows': [[...]], 'headers': [...]}
                - {'type': 'divider'}

        Returns:
            Full formatted description string
        """
        parts = []

        for section in sections:
            section_type = section.get('type')

            if section_type == 'heading':
                parts.append(f"h2. {section['text']}")

            elif section_type == 'subheading':
                parts.append(f"h3. {section['text']}")

            elif section_type == 'text':
                parts.append(section['text'])

            elif section_type == 'table':
                table = self.build_table(
                    rows=section['rows'],
                    headers=section.get('headers')
                )
                parts.append(table)

            elif section_type == 'divider':
                parts.append("----")

        return "\n\n".join(parts)

    def create_story(self, project_key, summary, description="", **kwargs):
        """
        Create a Jira story with optional fields.

        Args:
            project_key: Project key (e.g., 'PROJ')
            summary:     Story summary/title
            description: Story description (plain text or wiki markup)
            **kwargs:    Optional fields:
                           priority   - e.g. 'High'
                           labels     - e.g. ['backend', 'security']
                           assignee   - e.g. 'john.doe'
                           comments   - list of comment strings to add after creation
                           attachments - list of file paths to attach after creation

        Returns:
            Created issue dict, or None on failure
        """
        endpoint = f"{self.jira_url}/rest/api/2/issue"

        payload = {
            "fields": {
                "project":     {"key": project_key},
                "summary":     summary,
                "description": description,
                "issuetype":   {"name": "Story"}
            }
        }

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
                issue_key = result.get('key')
                print(f"✓ Story created: {issue_key}")
                print(f"  URL: {self.jira_url}/browse/{issue_key}")

                # Add comments if provided
                if "comments" in kwargs and kwargs["comments"]:
                    for comment in kwargs["comments"]:
                        self.add_comment(issue_key, comment)

                # Add attachments if provided
                if "attachments" in kwargs and kwargs["attachments"]:
                    for file_path in kwargs["attachments"]:
                        self.add_attachment(issue_key, file_path)

                return result
            else:
                print(f"✗ Failed to create story: {response.status_code}")
                print(f"  Error: {response.text}")
                return None

        except Exception as e:
            print(f"✗ Error creating story: {e}")
            return None

    def add_comment(self, issue_key, comment):
        """
        Add a comment to an existing Jira issue.

        Args:
            issue_key: Jira issue key (e.g., 'PROJ-123')
            comment:   Comment text (plain text or wiki markup)

        Returns:
            Created comment dict, or None on failure
        """
        endpoint = f"{self.jira_url}/rest/api/2/issue/{issue_key}/comment"

        payload = {
            "body": comment
        }

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
                print(f"  ✓ Comment added to {issue_key} (ID: {result.get('id')})")
                return result
            else:
                print(f"  ✗ Failed to add comment to {issue_key}: {response.status_code}")
                print(f"    Error: {response.text}")
                return None

        except Exception as e:
            print(f"  ✗ Error adding comment: {e}")
            return None

    def add_attachment(self, issue_key, file_path):
        """
        Add a file attachment to an existing Jira issue.

        Args:
            issue_key: Jira issue key (e.g., 'PROJ-123')
            file_path: Full path to the file to attach

        Returns:
            Attachment response dict, or None on failure
        """
        # Validate file exists before attempting upload
        if not os.path.exists(file_path):
            print(f"  ✗ File not found: {file_path}")
            return None

        endpoint = f"{self.jira_url}/rest/api/2/issue/{issue_key}/attachments"

        # Attachment upload requires a different header set -
        # no Content-Type (requests sets multipart boundary automatically)
        # but X-Atlassian-Token must be set to suppress XSRF check
        attachment_headers = {
            "Authorization": self.headers["Authorization"],
            "X-Atlassian-Token": "no-check"
        }

        file_name = os.path.basename(file_path)

        try:
            with open(file_path, "rb") as f:
                response = requests.post(
                    endpoint,
                    headers=attachment_headers,
                    files={"file": (file_name, f)},
                    verify=self.cert_path,
                    timeout=30  # Larger timeout for file uploads
                )

            if response.status_code == 200:
                result = response.json()
                # Response is a list of attachment objects
                attachment = result[0] if isinstance(result, list) else result
                print(f"  ✓ Attached '{file_name}' to {issue_key}")
                print(f"    Size: {attachment.get('size', 'unknown')} bytes")
                return result
            else:
                print(f"  ✗ Failed to attach '{file_name}' to {issue_key}: {response.status_code}")
                print(f"    Error: {response.text}")
                return None

        except Exception as e:
            print(f"  ✗ Error attaching file: {e}")
            return None

    def add_attachments(self, issue_key, file_paths):
        """
        Add multiple file attachments to an existing Jira issue.

        Args:
            issue_key:  Jira issue key (e.g., 'PROJ-123')
            file_paths: List of file paths to attach

        Returns:
            List of results for each attachment attempt
        """
        results = []
        for file_path in file_paths:
            result = self.add_attachment(issue_key, file_path)
            results.append(result)
        return results


# ── Example usage ─────────────────────────────────────────────────────────────

if __name__ == "__main__":

    creator = JiraStoryCreator(
        jira_url="https://your-server:8443",
        pat_token="your-personal-access-token",
        cert_path="/path/to/certificate.pem"
    )

    if creator.test_connection():

        # Build description with tables
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
                ]
            },
            {
                'type': 'divider'
            },
            {
                'type': 'heading',
                'text': 'Story Info'
            },
            {
                'type': 'table',
                'rows': [
                    ['Release',       'Q1 2026'],
                    ['Team',          'Platform'],
                    ['Story Points',  '5'],
                ]
            },
        ])

        # ── Option A: Pass comments and attachments into create_story ──────────
        story = creator.create_story(
            project_key="PROJ",
            summary="Implement user authentication module",
            description=description,
            priority="High",
            labels=["backend", "security"],
            comments=[
                "Initial story created via API.",
                "Design mockups have been reviewed and approved."
            ],
            attachments=[
                "/path/to/mockup.png",
                "/path/to/requirements.pdf"
            ]
        )

        # ── Option B: Add comments and attachments separately after creation ───
        if story:
            issue_key = story.get('key')

            # Single comment
            creator.add_comment(issue_key, "Follow-up comment added separately.")

            # Single attachment
            creator.add_attachment(issue_key, "/path/to/diagram.png")

            # Multiple attachments at once
            creator.add_attachments(issue_key, [
                "/path/to/file1.pdf",
                "/path/to/file2.xlsx"
            ])
