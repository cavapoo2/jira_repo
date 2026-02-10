def build_table(self, rows, headers=None):
    """
    Build a Jira wiki markup table

    Args:
        rows: List of row lists
              e.g. [["Item 1", "Done", "All good"],
                    ["Item 2", "In Progress", "Ongoing"]]
        headers: Optional list of column header strings
                 e.g. ["Name", "Status", "Notes"]
                 If omitted, table renders with no header row

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
        # Determine column count from headers if available, else from first row
        col_count = len(headers) if headers else len(rows[0])

        # Pad row with empty strings if fewer cells than columns
        padded_row = row + [""] * (col_count - len(row))
        table_rows.append("| " + " | ".join(str(cell) for cell in padded_row) + " |")

    return "\n".join(table_rows)
