# Hybrid Retrieval

## Overview
The `HybridRetriever` (`src/rag/retrieval/hybrid.py`) combines the strengths of the `DenseRetriever` (semantic understanding) and `SparseRetriever` (exact lexical matching).

## Architecture
```
Query 
  ├─> Dense Retriever (top N)
  └─> Sparse Retriever (top N)
         │
         ▼
 Candidate Fusion (RRF)
         │
         ▼
 Combined Top-K Candidates
```

## Candidate Fusion Strategy
We utilize **Reciprocal Rank Fusion (RRF)** to combine the results.
- **Why RRF?** Dense (cosine distance) and Sparse (BM25) scores are not on the same scale and have completely different distributions. Trying to normalize and sum them using a weighted $\alpha$ parameter is brittle and highly dependent on the corpus. RRF relies purely on the *rank* returned by each system.
- **Formula:** `RRF_Score = 1.0 / (k + rank_dense) + 1.0 / (k + rank_sparse)`
- **Parameter:** We use the standard $k=60$.

## Experimental Results
Tests were created to contrast the failure modes of isolated retrieval methods:
- **Dense Only:** Failed to rank exact machine IDs correctly when heavily surrounded by distinct context.
- **Sparse Only:** Failed completely to find semantic matches for "hot" when the document stated "temperature 50C".
- **Hybrid (RRF):** Consistently ranked the optimal document at position 1 across both semantic queries and exact entity lookup queries, validating the fusion approach.
