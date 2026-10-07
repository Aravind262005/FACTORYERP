import pytest
from src.rag.ingestion.models import ParsedDocument, ParsedSection, ParsedElement
from src.rag.chunking import HierarchicalChunker

def test_hierarchical_chunker_basic():
    # Construct a mock parsed document
    doc = ParsedDocument(
        document_id="SOP-014",
        sections=[
            ParsedSection(
                title="1. Introduction",
                level=1,
                elements=[
                    ParsedElement(element_type="text", text="This is intro.", page=1)
                ],
                subsections=[
                    ParsedSection(
                        title="1.1 Scope",
                        level=2,
                        elements=[
                            ParsedElement(element_type="text", text="Scope is wide.", page=1)
                        ],
                        page=1
                    )
                ],
                page=1
            )
        ],
        metadata={
            "document_type": "SOP",
            "source_file": "sop014.md",
            "revision": "v2"
        }
    )
    
    chunker = HierarchicalChunker(max_chunk_size=100)
    chunks = chunker.chunk_document(doc)
    
    # We expect:
    # 1. Parent chunk for "1. Introduction" (S1)
    # 2. Child chunk for "1. Introduction" text (S1-C001)
    # 3. Parent chunk for "1.1 Scope" (S2) with parent_id = S1
    # 4. Child chunk for "1.1 Scope" text (S2-C001)
    
    assert len(chunks) == 4
    
    # Verify parents and children
    intro_parent = next(c for c in chunks if c.chunk_id == "SOP-014-S1-C000")
    assert intro_parent.parent_id is None
    assert "This is intro." in intro_parent.text
    
    intro_child = next(c for c in chunks if c.chunk_id == "SOP-014-S1-C001")
    assert intro_child.parent_id == "SOP-014-S1-C000"
    assert intro_child.text == "This is intro."
    assert intro_child.revision == "v2"
    
    scope_parent = next(c for c in chunks if c.chunk_id == "SOP-014-S2-C000")
    assert scope_parent.parent_id == "SOP-014-S1-C000"
    
    scope_child = next(c for c in chunks if c.chunk_id == "SOP-014-S2-C001")
    assert scope_child.parent_id == "SOP-014-S2-C000"
    assert scope_child.text == "Scope is wide."
    
def test_hierarchical_chunker_tables_and_warnings():
    doc = ParsedDocument(
        document_id="SOP-015",
        sections=[
            ParsedSection(
                title="Warnings and Tables",
                level=1,
                elements=[
                    ParsedElement(element_type="warning", text="**WARNING**: Hot", page=1),
                    ParsedElement(element_type="table", text="Row 1: A=1", page=2)
                ],
                page=1
            )
        ],
        metadata={
            "document_type": "SOP",
            "source_file": "sop015.md"
        }
    )
    
    chunker = HierarchicalChunker(max_chunk_size=500)
    chunks = chunker.chunk_document(doc)
    
    # Expected:
    # 1. Parent S1-C000
    # 2. Child warning S1-C001
    # 3. Child table S1-C002 (since tables and warnings are split into own chunks)
    assert len(chunks) == 3
    
    warning_chunk = chunks[1]
    assert warning_chunk.text == "**WARNING**: Hot"
    assert warning_chunk.page == 1
    
    table_chunk = chunks[2]
    assert table_chunk.text == "Row 1: A=1"
    assert table_chunk.page == 2
