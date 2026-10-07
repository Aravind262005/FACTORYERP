from typing import List
from .models import ParsedElement, ParsedSection, ParsedDocument

class StructureParser:
    def parse(self, elements: List[ParsedElement], document_id: str, metadata: dict) -> ParsedDocument:
        """Groups a flat list of elements into a hierarchical section tree."""
        root_sections = []
        section_stack = []
        
        # A dummy root section if elements appear before any heading
        current_section = ParsedSection(title="Document Start", level=0, elements=[], page=1)
        
        for el in elements:
            if el.element_type == "heading":
                level = el.metadata.get("level", 1)
                new_sec = ParsedSection(title=el.text, level=level, elements=[], page=el.page)
                
                if not section_stack:
                    if current_section.elements:
                        root_sections.append(current_section)
                    root_sections.append(new_sec)
                    section_stack = [new_sec]
                else:
                    # Pop until we find a parent with level < new level
                    while section_stack and section_stack[-1].level >= level:
                        section_stack.pop()
                        
                    if not section_stack:
                        root_sections.append(new_sec)
                        section_stack = [new_sec]
                    else:
                        section_stack[-1].subsections.append(new_sec)
                        section_stack.append(new_sec)
                
                current_section = new_sec
            else:
                current_section.elements.append(el)
                
        if not root_sections:
            root_sections.append(current_section)
            
        return ParsedDocument(
            document_id=document_id,
            sections=root_sections,
            metadata=metadata
        )
