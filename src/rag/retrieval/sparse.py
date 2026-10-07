import re
import math
from typing import List, Dict, Any, Optional
from rank_bm25 import BM25Okapi
from ..schema import ChunkMetadata

def tokenize(text: str) -> List[str]:
    """Basic tokenizer that preserves alphanumeric tokens, good for manufacturing IDs."""
    text = text.lower()
    return re.findall(r'[a-z0-9]+', text)

class SparseRetriever:
    def __init__(self):
        self.chunks = []
        self.bm25 = None
        self.tokenized_corpus = []
        self.token_sets = []

    def index_chunks(self, chunks: List[ChunkMetadata]):
        """Re-indexes the entire corpus for BM25."""
        if not chunks:
            return
            
        # BM25 operates in memory for this implementation. 
        # In a real heavy-duty setup, we'd use Elasticsearch or an inverted index on disk.
        self.chunks = chunks
        self.tokenized_corpus = [tokenize(c.text) for c in chunks]
        self.token_sets = [set(tokens) for tokens in self.tokenized_corpus]
        
        # We use BM25Okapi. Note that it can give negative scores for terms in >50% of docs,
        # but it guarantees 0 for non-matching terms.
        self.bm25 = BM25Okapi(self.tokenized_corpus)

    def search(self, query: str, top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        if not self.bm25 or not self.chunks:
            return []
            
        tokenized_query = tokenize(query)
        query_set = set(tokenized_query)
        scores = self.bm25.get_scores(tokenized_query)
        
        # Pair scores with chunks
        scored_chunks = []
        for i, chunk in enumerate(self.chunks):
            # Apply hard filters if any
            if filters:
                match = True
                for k, v in filters.items():
                    # Support metadata filtering on the chunk level
                    if getattr(chunk, k, None) != v:
                        match = False
                        break
                if not match:
                    continue
                    
            # Only consider documents that actually share a token with the query
            if query_set.intersection(self.token_sets[i]):
                scored_chunks.append({
                    "chunk_id": chunk.chunk_id,
                    "text": chunk.text,
                    "score": float(scores[i]),
                    "metadata": chunk.model_dump(exclude_none=True),
                    "chunk_obj": chunk
                })

        # Sort descending by score
        scored_chunks.sort(key=lambda x: x["score"], reverse=True)
        
        # Remove the object ref before returning for consistency with dense retriever
        for sc in scored_chunks:
            sc.pop("chunk_obj", None)
            
        return scored_chunks[:top_k]
