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
    path = str(tmp_path / "chroma_test_db4")
    yield path
    if os.path.exists(path):
        shutil.rmtree(path, ignore_errors=True)

def test_query_analyzer():
    analyzer = QueryAnalyzer()
    
    # Test strict machine filter
    strict, soft = analyzer.analyze("What is the maintenance for M04?")
    assert strict == {"machine_id": "M04"}
    assert soft == {}
    
    # Test strict doc filter
    strict, soft = analyzer.analyze("Refer to SOP-14 for details.")
    assert strict == {"document_id": "SOP-14"}
    assert soft == {"document_type": "SOP"}
    
    # Test soft document type filter
    strict, soft = analyzer.analyze("Where is the safety guide?")
    assert strict == {}
    assert soft == {"document_type": "MANUAL"} # 'guide' matches first

def test_metadata_aware_retrieval(temp_db_path):
    dense = DenseRetriever(db_path=temp_db_path, collection_name="test_meta")
    sparse = SparseRetriever()
    hybrid = HybridRetriever(dense, sparse)
    
    chunks = [
        ChunkMetadata(
            document_id="SOP-01", chunk_id="C1", text="Machine M04 maximum temperature is 50C.", 
            document_type="SOP", machine_id="M04", authority_level="current", source_file="sop01.pdf"
        ),
        ChunkMetadata(
            document_id="MAN-02", chunk_id="C2", text="The cooling unit should not exceed 45C.", 
            document_type="MANUAL", machine_id="M05", authority_level="current", source_file="man02.pdf"
        ),
        ChunkMetadata(
            document_id="MAN-02", chunk_id="C3", text="General maintenance for M04 requires checking the cooling unit.", 
            document_type="MANUAL", machine_id="M04", authority_level="current", source_file="man02.pdf"
        )
    ]
    hybrid.index_chunks(chunks)
    
    analyzer = QueryAnalyzer()
    query = "cooling unit for M04"
    strict, soft = analyzer.analyze(query)
    
    # Verify strict filter restricts results
    res = hybrid.search(query, top_k=5, filters=strict, soft_filters=soft)
    
    # M05's cooling unit chunk (C2) should be completely filtered out by strict machine_id="M04"
    cids = [r["chunk_id"] for r in res]
    assert "C2" not in cids
    assert "C3" in cids
    assert "C1" in cids
    
    # Test soft filter
    query2 = "What is the maintenance procedure?"
    strict2, soft2 = analyzer.analyze(query2)
    assert soft2.get("document_type") == "SOP"
    
    # Both C1 and C3 mention maintenance/temperature. SOP should be boosted.
    res2 = hybrid.search(query2, top_k=2, filters=strict2, soft_filters=soft2)
    
    # SOP-01 (C1) should get a boost
    assert res2[0]["metadata"]["document_type"] == "SOP"
