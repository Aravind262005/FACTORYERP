import pytest
from src.rag.schema import ChunkMetadata
from src.rag.retrieval.dense import DenseRetriever
from src.rag.retrieval.sparse import SparseRetriever
import os
import shutil

@pytest.fixture
def temp_db_path(tmp_path):
    path = str(tmp_path / "chroma_test_db2")
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

def test_sparse_vs_dense(temp_db_path, test_chunks):
    dense = DenseRetriever(db_path=temp_db_path, collection_name="test_dense")
    dense.index_chunks(test_chunks)
    
    sparse = SparseRetriever()
    sparse.index_chunks(test_chunks)
    
    # Query: Exact terminology "M04"
    query_exact = "M04"
    
    res_dense = dense.search(query_exact, top_k=2)
    res_sparse = sparse.search(query_exact, top_k=2)
    
    # Dense might struggle to distinguish M04 vs M05 if they are just random tokens to the model,
    # but BM25 will strictly match M04.
    
    # Let's check Recall@2 for M04
    dense_ids = [r["chunk_id"] for r in res_dense]
    sparse_ids = [r["chunk_id"] for r in res_sparse]
    
    assert "C1" in sparse_ids
    assert "C3" in sparse_ids
    assert "C4" not in sparse_ids # M05 and M06, no M04
    
    # Query: Semantic paraphrase "How hot can the equipment get?"
    query_semantic = "How hot can the equipment get?"
    
    res_dense_sem = dense.search(query_semantic, top_k=2)
    res_sparse_sem = sparse.search(query_semantic, top_k=2)
    
    # Dense should find C1 and C2 easily due to "temperature", "hot", "cooling".
    # Sparse will likely fail or score 0 since exact words don't match.
    sparse_sem_ids = [r["chunk_id"] for r in res_sparse_sem]
    dense_sem_ids = [r["chunk_id"] for r in res_dense_sem]
    
    assert "C2" in sparse_sem_ids # Matches "the"
    assert "C1" not in sparse_sem_ids # "temperature" and "50c" don't match exactly
    
    assert "C1" in dense_sem_ids or "C2" in dense_sem_ids
