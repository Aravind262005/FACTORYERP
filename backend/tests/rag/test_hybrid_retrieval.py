import pytest
from src.rag.schema import ChunkMetadata
from src.rag.retrieval.dense import DenseRetriever
from src.rag.retrieval.sparse import SparseRetriever
from src.rag.retrieval.hybrid import HybridRetriever
import os
import shutil

@pytest.fixture
def temp_db_path(tmp_path):
    path = str(tmp_path / "chroma_test_db3")
    yield path
    if os.path.exists(path):
        shutil.rmtree(path, ignore_errors=True)

@pytest.fixture
def test_chunks():
    return [
        ChunkMetadata(
            document_id="SOP-01", chunk_id="C1", text="Machine M04 maximum temperature is 50C.", 
            document_type="SOP", authority_level="current", source_file="sop01.pdf"
        ),
        ChunkMetadata(
            document_id="SOP-01", chunk_id="C2", text="The cooling unit should not exceed 45C.", 
            document_type="SOP", authority_level="current", source_file="sop01.pdf"
        ),
        ChunkMetadata(
            document_id="MAN-02", chunk_id="C3", text="For M04 maintenance, refer to ISO-9001 standard procedures.", 
            document_type="MANUAL", authority_level="current", source_file="man02.pdf"
        ),
        ChunkMetadata(
            document_id="POL-03", chunk_id="C4", text="All machines including M05 and M06 require daily checks.", 
            document_type="POLICY", authority_level="current", source_file="pol03.pdf"
        )
    ]

def test_hybrid_retrieval(temp_db_path, test_chunks):
    dense = DenseRetriever(db_path=temp_db_path, collection_name="test_hybrid")
    sparse = SparseRetriever()
    hybrid = HybridRetriever(dense, sparse)
    
    hybrid.index_chunks(test_chunks)
    
    # Query: "What is the maintenance protocol for M04?"
    # Dense should like C3 (maintenance, protocol) but also maybe C4 (daily checks).
    # Sparse should like C3 (M04, maintenance) and C1 (M04).
    # Hybrid should rank C3 highest.
    
    query = "What is the maintenance protocol for M04?"
    
    dense_res = dense.search(query, top_k=1)
    sparse_res = sparse.search(query, top_k=1)
    hybrid_res = hybrid.search(query, top_k=1)
    
    # Check that hybrid returns C3
    assert len(hybrid_res) == 1
    assert hybrid_res[0]["chunk_id"] == "C3"
    assert "rrf_score" in hybrid_res[0]
    
    # Query: "temperature M04"
    # Should get C1 highest
    hybrid_res2 = hybrid.search("temperature M04", top_k=1)
    assert hybrid_res2[0]["chunk_id"] == "C1"
