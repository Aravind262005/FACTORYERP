import pytest
from src.rag.schema import ChunkMetadata
from src.rag.retrieval.dense import DenseRetriever
import os
import shutil

@pytest.fixture
def temp_db_path(tmp_path):
    path = str(tmp_path / "chroma_test_db")
    yield path
    if os.path.exists(path):
        shutil.rmtree(path)

@pytest.fixture
def retriever(temp_db_path):
    return DenseRetriever(db_path=temp_db_path, collection_name="test_collection")

def test_dense_indexing_and_search(retriever):
    chunks = [
        ChunkMetadata(
            document_id="SOP-01", chunk_id="SOP-01-C1", text="Machine M01 maximum temperature is 50C.", 
            document_type="SOP", authority_level="current", source_file="sop01.pdf"
        ),
        ChunkMetadata(
            document_id="SOP-01", chunk_id="SOP-01-C2", text="Alloy steel must be stored in a dry place.", 
            document_type="SOP", authority_level="current", source_file="sop01.pdf"
        ),
        ChunkMetadata(
            document_id="MAN-02", chunk_id="MAN-02-C1", text="For M01 maintenance, turn off power first.", 
            document_type="MANUAL", authority_level="current", source_file="man02.pdf"
        )
    ]
    
    # 1. Test indexing
    res = retriever.index_chunks(chunks)
    assert res["added"] == 3
    assert res["ignored"] == 0
    
    # 2. Test duplicate prevention
    res2 = retriever.index_chunks([chunks[0]])
    assert res2["added"] == 0
    assert res2["ignored"] == 1
    
    # 3. Test basic search
    results = retriever.search("What is the max temp for M01?", top_k=2)
    assert len(results) == 2
    assert results[0]["chunk_id"] == "SOP-01-C1"
    
    # 4. Test filtering
    filtered_results = retriever.search("M01", top_k=5, filters={"document_type": "MANUAL"})
    assert len(filtered_results) == 1
    assert filtered_results[0]["chunk_id"] == "MAN-02-C1"
    
    # 5. Test deletion
    retriever.delete_document("SOP-01")
    search_after_del = retriever.search("Alloy steel", top_k=5)
    # Shouldn't find SOP-01 chunks
    for r in search_after_del:
        assert r["metadata"]["document_id"] != "SOP-01"
