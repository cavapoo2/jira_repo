def build_description(self, sections):
    """
    Build a full description with multiple sections, text, and tables.

    Args:
        sections: List of dicts, each with a 'type' key:
            - {'type': 'heading',    'text': 'My Heading'}
            - {'type': 'subheading', 'text': 'My Subheading'}
            - {'type': 'text',       'text': 'Some paragraph text'}
            - {'type': 'table',      'rows': [[...]], 'headers': [...]}  # headers optional
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
                headers=section.get('headers')  # .get() returns None if not present
            )
            parts.append(table)

        elif section_type == 'divider':
            parts.append("----")

    return "\n\n".join(parts)
