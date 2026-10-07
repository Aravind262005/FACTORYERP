from typing import List, Dict, Any, Optional
from .dense import DenseRetriever
from .sparse import SparseRetriever
from ..schema import ChunkMetadata

class HybridRetriever:
    def __init__(self, dense_retriever: DenseRetriever, sparse_retriever: SparseRetriever, rrf_k: int = 60):
        self.dense = dense_retriever
        self.sparse = sparse_retriever
        self.rrf_k = rrf_k

    def index_chunks(self, chunks: List[ChunkMetadata]):
        """Indexes chunks into both dense and sparse retrievers."""
        self.dense.index_chunks(chunks)
        self.sparse.index_chunks(chunks)

    def search(self, query: str, top_k: int = 5, filters: Optional[Dict[str, Any]] = None, soft_filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Performs Hybrid Search using Reciprocal Rank Fusion (RRF).
        Applies strict `filters` directly to underlying retrievers.
        Applies `soft_filters` by boosting the RRF score of matching candidates.
        """
        if filters is None:
            filters = {}
        else:
            filters = filters.copy()
            
        # Authority handling: default to only current documents unless historical intent is detected
        historical_intent = filters.pop("historical_intent", False)
        if not historical_intent and "authority_level" not in filters:
            filters["authority_level"] = "current"

        pool_size = max(top_k * 2, 20)
        
        dense_results = self.dense.search(query, top_k=pool_size, filters=filters)
        sparse_results = self.sparse.search(query, top_k=pool_size, filters=filters)
        
        # Reciprocal Rank Fusion
        fused_scores = {}
        chunk_map = {}
        
        # Process dense
        for rank, res in enumerate(dense_results):
            cid = res["chunk_id"]
            chunk_map[cid] = res
            fused_scores[cid] = 1.0 / (self.rrf_k + rank + 1)
            
        # Process sparse
        for rank, res in enumerate(sparse_results):
            cid = res["chunk_id"]
            if cid not in chunk_map:
                chunk_map[cid] = res
                fused_scores[cid] = 0.0
            fused_scores[cid] += 1.0 / (self.rrf_k + rank + 1)
            
        # Apply Soft Prioritization
        if soft_filters:
            for cid, score in fused_scores.items():
                metadata = chunk_map[cid].get("metadata", {})
                match_bonus = 0.0
                for k, v in soft_filters.items():
                    if metadata.get(k) == v:
                        match_bonus += 0.5 # Substantial boost to push it up the rankings
                fused_scores[cid] += match_bonus
                
        # Sort combined
        sorted_cids = sorted(fused_scores.keys(), key=lambda k: fused_scores[k], reverse=True)
        
        # Build final output
        final_results = []
        for cid in sorted_cids[:top_k]:
            res = chunk_map[cid].copy()
            res["rrf_score"] = fused_scores[cid]
            res["retrieval_method"] = "hybrid"
            final_results.append(res)
            
        return final_results
