import pytest
from src.rag.retrieval.reranker import Reranker

def test_reranker():
    reranker = Reranker()
    
    # Pre-tend hybrid returned these two
    # C1 is lexically closer but semantically slightly off
    # C2 is perfectly answering the question
    
    query = "How often should I clean the coolant filter?"
    
    candidates = [
        {"chunk_id": "C1", "text": "The coolant filter is located on the side. Clean the surrounding area.", "rrf_score": 0.05},
        {"chunk_id": "C2", "text": "The coolant filter must be cleaned every 48 hours of operation.", "rrf_score": 0.04}
    ]
    
    # Reranker should re-score and realize C2 is the actual answer
    # Note: CrossEncoder download might take a few seconds on first run
    reranked = reranker.rerank(query, candidates, top_k=2)
    
    assert len(reranked) == 2
    assert "cross_encoder_score" in reranked[0]
    
    # If the model loaded, it should rank C2 higher
    if reranker.model is not None:
        assert reranked[0]["chunk_id"] == "C2"
        assert reranked[1]["chunk_id"] == "C1"
