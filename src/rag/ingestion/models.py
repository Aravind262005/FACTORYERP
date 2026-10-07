from pydantic import BaseModel
from typing import List, Optional, Any, Dict

class ParsedElement(BaseModel):
    element_type: str # 'heading', 'text', 'table', 'warning', 'note', 'list_item'
    text: str
    page: int
    metadata: Dict[str, Any] = {}

class ParsedSection(BaseModel):
    title: str
    level: int
    elements: List[ParsedElement]
    subsections: List['ParsedSection'] = []
    page: int

class ParsedDocument(BaseModel):
    document_id: str
    sections: List[ParsedSection]
    metadata: Dict[str, Any]
