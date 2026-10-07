import re
from typing import List, Dict, Any
from .models import ParsedElement, ParsedSection

def parse_markdown_table(table_text: str, title: str = "") -> str:
    """Converts a markdown table into a retrieval-friendly format."""
    lines = table_text.strip().split('\n')
    if len(lines) < 2:
        return table_text
    
    headers = [h.strip() for h in lines[0].split('|') if h.strip()]
    
    # Check if second line is separator
    start_idx = 1
    if '---' in lines[1]:
        start_idx = 2
        
    structured_rows = []
    if title:
        structured_rows.append(f"Table: {title}")
        
    for i in range(start_idx, len(lines)):
        row_cells = [c.strip() for c in lines[i].split('|') if c.strip()]
        row_str_parts = []
        for j, cell in enumerate(row_cells):
            header = headers[j] if j < len(headers) else f"Column {j+1}"
            row_str_parts.append(f"{header} = {cell}")
        structured_rows.append(f"Row {i - start_idx + 1}: " + ", ".join(row_str_parts))
        
    return "\n".join(structured_rows)

class MarkdownExtractor:
    """A structure-aware extractor for Markdown text.
    Simulates layout extraction by parsing headings, tables, warnings, and pages.
    """
    
    def extract(self, text: str, default_page: int = 1) -> List[ParsedElement]:
        elements = []
        current_page = default_page
        
        # Regex for different blocks
        page_break_re = re.compile(r'---PAGE (\d+)---')
        heading_re = re.compile(r'^(#{1,6})\s+(.*)')
        warning_re = re.compile(r'^\*\*(WARNING|NOTE|CAUTION)\*\*:\s*(.*)')
        
        lines = text.split('\n')
        
        in_table = False
        table_lines = []
        table_title = ""
        
        for line in lines:
            # Handle table state
            if '|' in line and not in_table:
                in_table = True
                table_lines = [line]
                continue
            elif in_table and '|' in line:
                table_lines.append(line)
                continue
            elif in_table and not '|' in line:
                in_table = False
                parsed_table = parse_markdown_table("\n".join(table_lines), table_title)
                elements.append(ParsedElement(
                    element_type="table", text=parsed_table, page=current_page, metadata={"original_title": table_title}
                ))
                table_lines = []
                table_title = ""
                # Proceed to process the current line
                
            page_match = page_break_re.match(line.strip())
            if page_match:
                current_page = int(page_match.group(1))
                continue
                
            if not line.strip():
                continue
                
            head_match = heading_re.match(line)
            if head_match:
                level = len(head_match.group(1))
                elements.append(ParsedElement(
                    element_type="heading", text=head_match.group(2), page=current_page, metadata={"level": level}
                ))
                continue

            # Table title heuristic (line right before table)
            if line.strip().startswith("Table:"):
                table_title = line.strip()
                # We'll also add it as text just in case it's a standalone line
                elements.append(ParsedElement(element_type="text", text=line.strip(), page=current_page))
                continue
                
            warn_match = warning_re.match(line.strip())
            if warn_match:
                elements.append(ParsedElement(
                    element_type="warning", text=line.strip(), page=current_page, metadata={"type": warn_match.group(1)}
                ))
                continue
                
            if line.strip().startswith('- ') or line.strip().startswith('* '):
                elements.append(ParsedElement(
                    element_type="list_item", text=line.strip(), page=current_page
                ))
                continue
                
            elements.append(ParsedElement(
                element_type="text", text=line.strip(), page=current_page
            ))
            
        if in_table:
             parsed_table = parse_markdown_table("\n".join(table_lines), table_title)
             elements.append(ParsedElement(
                 element_type="table", text=parsed_table, page=current_page, metadata={"original_title": table_title}
             ))
             
        return elements
