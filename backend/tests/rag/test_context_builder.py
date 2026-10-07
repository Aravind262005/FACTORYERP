import pytest
from src.rag.schema import ChunkMetadata
from src.rag.retrieval.dense import DenseRetriever
from src.rag.retrieval.context_builder import ContextBuilder
import os
import shutil

@pytest.fixture
def temp_db_path(tmp_path):
    path = str(tmp_path / "chroma_test_db6")
    yield path
    if os.path.exists(path):
        shutil.rmtree(path, ignore_errors=True)

def test_context_builder(temp_db_path):
    dense = DenseRetriever(db_path=temp_db_path, collection_name="test_context")
    
    # 1 Parent, 2 Children
    chunks = [
        ChunkMetadata(
            document_id="SOP-01", chunk_id="SOP-01-S1-C000", text="Section 1: Engine M04 specifications.", 
            document_type="SOP", authority_level="current", source_file="sop01.pdf"
        ),
        ChunkMetadata(
            document_id="SOP-01", chunk_id="SOP-01-S1-C001", parent_id="SOP-01-S1-C000", text="Max temp is 50C.", 
            document_type="SOP", authority_level="current", source_file="sop01.pdf"
        ),
        ChunkMetadata(
            document_id="SOP-01", chunk_id="SOP-01-S1-C002", parent_id="SOP-01-S1-C000", text="Min temp is 10C.", 
            document_type="SOP", authority_level="current", source_file="sop01.pdf"
        ),
        ChunkMetadata(
            document_id="SOP-02", chunk_id="SOP-02-C1", text="No parent chunk for this one.", 
            document_type="SOP", authority_level="current", source_file="sop02.pdf"
        )
    ]
    dense.index_chunks(chunks)
    
    builder = ContextBuilder(dense)
    
    # Scenario 1: Top candidates are the two children
    candidates = [
        {"chunk_id": "SOP-01-S1-C001", "metadata": {"parent_id": "SOP-01-S1-C000"}},
        {"chunk_id": "SOP-01-S1-C002", "metadata": {"parent_id": "SOP-01-S1-C000"}},
        {"chunk_id": "SOP-02-C1", "metadata": {}}
    ]
    
    expanded = builder.expand_context(candidates)
    
    # Expected: The two children merge into the single parent. SOP-02-C1 stays standalone.
    # Total length should be 2.
    assert len(expanded) == 2
    
    # First chunk should be the parent
    assert expanded[0]["chunk_id"] == "SOP-01-S1-C000"
    assert "Engine M04 specifications." in expanded[0]["text"]
    assert expanded[0].get("expanded") is True
    
    # Second chunk should be the standalone
    assert expanded[1]["chunk_id"] == "SOP-02-C1"
    
    # Scenario 2: Parent is missing in DB (fallback test)
    candidates2 = [
        {"chunk_id": "MISSING-C001", "metadata": {"parent_id": "MISSING-C000"}, "text": "I am an orphan."}
    ]
    expanded2 = builder.expand_context(candidates2)
    assert len(expanded2) == 1
    assert expanded2[0]["chunk_id"] == "MISSING-C001" # Kept original
