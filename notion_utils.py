import re
from typing import List, Dict, Any


def parse_inline_formatting(text: str) -> List[Dict[str, Any]]:
    """Convert inline markdown formatting to Notion rich text objects"""
    # Remove citation references like [4], [1], etc.
    text = re.sub(r'\[\d+\]', '', text)

    segments = []
    current_pos = 0

    patterns = [
        # URLs (must come before markdown links)
        (r'(https?://\S+)', lambda m: {"type": "text", "text": {"content": m.group(1), 
                                                               "link": {"url": m.group(1)}}}),
        # Bold + Italic
        (r'\*\*\*(.*?)\*\*\*', lambda m: {"type": "text", "text": {"content": m.group(1)}, 
                                         "annotations": {"bold": True, "italic": True}}),
        # Bold
        (r'\*\*(.*?)\*\*', lambda m: {"type": "text", "text": {"content": m.group(1)}, 
                                     "annotations": {"bold": True}}),
        # Italic
        (r'\*(.*?)\*', lambda m: {"type": "text", "text": {"content": m.group(1)}, 
                                 "annotations": {"italic": True}}),
        # Markdown Links
        (r'\[(.*?)\]\((.*?)\)', lambda m: {"type": "text", "text": {"content": m.group(1), 
                                                                    "link": {"url": m.group(2)}}}),
        # Inline Code
        (r'`(.*?)`', lambda m: {"type": "text", "text": {"content": m.group(1)}, 
                               "annotations": {"code": True}})
    ]

    while current_pos < len(text):
        earliest_match = None
        earliest_pattern = None
        earliest_pos = len(text)

        for pattern, formatter in patterns:
            match = re.search(pattern, text[current_pos:])
            if match and current_pos + match.start() < earliest_pos:
                earliest_match = match
                earliest_pattern = formatter
                earliest_pos = current_pos + match.start()

        if earliest_match and earliest_pattern:
            # Add text before the match
            if earliest_pos > current_pos:
                segments.append({
                    "type": "text",
                    "text": {"content": text[current_pos:earliest_pos]}
                })

            # Add the formatted text
            segments.append(earliest_pattern(earliest_match))
            current_pos = earliest_pos + len(earliest_match.group(0))
        else:
            # Add remaining text
            segments.append({
                "type": "text",
                "text": {"content": text[current_pos:]}
            })
            break

    return segments


def create_notion_blocks(markdown_text: str) -> List[Dict[str, Any]]:
    """Convert markdown text to Notion blocks"""
    blocks = []
    lines = markdown_text.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        # Skip empty lines
        if not line:
            i += 1
            continue

        # Headings
        if line.startswith('#'):
            heading_level = len(line.split()[0])
            if heading_level > 3:  # Notion only supports h1-h3
                heading_level = 3
            text_content = line.lstrip('#').strip()
            blocks.append({
                "object": "block",
                "type": f"heading_{heading_level}",
                f"heading_{heading_level}": {
                    "rich_text": parse_inline_formatting(text_content)
                }
            })

        # Bullet points
        elif line.startswith(('- ', '* ')):
            text_content = line[2:].strip()
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": parse_inline_formatting(text_content)
                }
            })

        # Numbered lists
        elif re.match(r'^\d+\.', line):
            text_content = re.sub(r'^\d+\.\s*', '', line)
            blocks.append({
                "object": "block",
                "type": "numbered_list_item",
                "numbered_list_item": {
                    "rich_text": parse_inline_formatting(text_content)
                }
            })

        # Code blocks
        elif line.startswith('```'):
            code_lines = []
            language = line[3:].strip()
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            blocks.append({
                "object": "block",
                "type": "code",
                "code": {
                    "rich_text": [{"type": "text", "text": {"content": '\n'.join(code_lines)}}],
                    "language": language if language else "plain text"
                }
            })

        # Regular paragraphs
        else:
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": parse_inline_formatting(line)
                }
            })

        i += 1

    return blocks


def split_by_headings(content: str) -> List[str]:
    """Split content into chunks by main headings"""
    chunks = []
    current_chunk = []

    for line in content.split('\n'):
        if line.startswith('# '):
            if current_chunk:
                chunks.append('\n'.join(current_chunk))
            current_chunk = [line]
        else:
            current_chunk.append(line)

    if current_chunk:
        chunks.append('\n'.join(current_chunk))

    return chunks


def add_content_to_notion(client, page_id: str, content: str):
    """Add markdown content to a Notion page with proper formatting"""
    blocks = create_notion_blocks(content)

    # Upload in batches of 1000 (Notion's maximum)
    for i in range(0, len(blocks), 1000):
        batch = blocks[i:i + 1000]
        client.blocks.children.append(
            block_id=page_id,
            children=batch
        )
