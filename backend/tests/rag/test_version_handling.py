import pytest
from src.rag.schema import ChunkMetadata
from src.rag.retrieval.dense import DenseRetriever
from src.rag.retrieval.sparse import SparseRetriever
from src.rag.retrieval.hybrid import HybridRetriever
from src.rag.query.analyzer import QueryAnalyzer
import os
import shutil

@pytest.fixture
def temp_db_path(tmp_path):
    path = str(tmp_path / "chroma_test_db5")
    yield path
    if os.path.exists(path):
        shutil.rmtree(path, ignore_errors=True)

def test_version_handling(temp_db_path):
    dense = DenseRetriever(db_path=temp_db_path, collection_name="test_versions")
    sparse = SparseRetriever()
    hybrid = HybridRetriever(dense, sparse)
    
    chunks = [
        ChunkMetadata(
            document_id="SOP-01", chunk_id="C1", text="Machine M04 max temp is 40C.", 
            document_type="SOP", machine_id="M04", authority_level="superseded", revision="v1", source_file="sop01_v1.pdf"
        ),
        ChunkMetadata(
            document_id="SOP-01", chunk_id="C2", text="Machine M04 max temp is 50C.", 
            document_type="SOP", machine_id="M04", authority_level="current", revision="v2", source_file="sop01_v2.pdf"
        )
    ]
    hybrid.index_chunks(chunks)
    
    analyzer = QueryAnalyzer()
    
    # 1. Standard query (should only return current)
    query = "What is the max temp for M04?"
    strict, soft = analyzer.analyze(query)
    res = hybrid.search(query, top_k=5, filters=strict, soft_filters=soft)
    
    assert len(res) == 1
    assert res[0]["chunk_id"] == "C2" # Only current is returned
    
    # 2. Historical query (should return both, but depends on search matching)
    query_hist = "What was the previous max temp for M04?"
    strict_hist, soft_hist = analyzer.analyze(query_hist)
    assert strict_hist.get("historical_intent") is True
    
    res_hist = hybrid.search(query_hist, top_k=5, filters=strict_hist, soft_filters=soft_hist)
    
    cids = [r["chunk_id"] for r in res_hist]
    assert "C1" in cids
    assert "C2" in cids
