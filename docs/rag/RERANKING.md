# Post-Retrieval Reranking

## Overview
While Hybrid Retrieval (Dense + Sparse) is excellent at surfacing a broad and deep candidate pool (high Recall), the top results are not always perfectly aligned with the exact nuance of the user's query. Post-Retrieval Reranking introduces a CrossEncoder to perform a highly accurate, pairwise evaluation between the user's query and the final candidates.

## Implementation Details
- **Reranker Engine:** (`src/rag/retrieval/reranker.py`) Uses the `sentence-transformers` CrossEncoder architecture.
- **Model:** `cross-encoder/ms-marco-MiniLM-L-6-v2`. This model was trained on the MS MARCO passage ranking dataset, making it ideal for QA and RAG pipelines.
- **Execution:**
  1. The Hybrid Retriever fetches a broad set of candidates.
  2. The candidates are passed to the `Reranker`.
  3. The Reranker constructs pairs: `(Query, Candidate_Text)`.
  4. The model outputs an exact relevance score for each pair.
  5. The candidates are sorted descending by this cross-encoder score.
- **Graceful Fallback:** If the `sentence-transformers` library or model fails to load, the Reranker gracefully returns the original candidate order (no-op), ensuring the RAG pipeline does not completely crash.
