def add_comment(self, issue_key, comment, comment_date=None):
    """
    Add a comment to an existing Jira issue.

    Args:
        issue_key:    Jira issue key (e.g., 'PROJ-123')
        comment:      Comment text (plain text or wiki markup)
        comment_date: Optional date string or datetime object to display
                      in the comment header (e.g., '2024-01-15' or datetime object)

    Returns:
        Created comment dict, or None on failure
    """
    endpoint = f"{self.jira_url}/rest/api/2/issue/{issue_key}/comment"

    # If a date is provided, prepend it to the comment body
    if comment_date:
        # Handle both string and datetime object
        if hasattr(comment_date, 'strftime'):
            formatted_date = comment_date.strftime("%d %B %Y")  # e.g. 15 January 2024
        else:
            formatted_date = comment_date

        # Build a clean header showing the backdated info
        date_header = self.build_description([
            {
                'type': 'table',
                'rows': [
                    ['*Date*',    formatted_date],
                    ['*Status*',  'Historical Entry'],
                ]
            },
            {
                'type': 'divider'
            }
        ])
        body = f"{date_header}\n\n{comment}"
    else:
        body = comment

    payload = {"body": body}

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
            date_info = f" (dated: {formatted_date})" if comment_date else ""
            print(f"  ✓ Comment added to {issue_key}{date_info} (ID: {result.get('id')})")
            return result
        else:
            print(f"  ✗ Failed to add comment to {issue_key}: {response.status_code}")
            print(f"    Error: {response.text}")
            return None

    except Exception as e:
        print(f"  ✗ Error adding comment: {e}")
        return None
