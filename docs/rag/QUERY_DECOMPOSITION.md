# Query Decomposition (Multi-Hop)

## Overview
Users frequently ask comparative or multi-hop questions (e.g., "Compare the maintenance schedule of M04 and M05"). A single dense vector search typically fails here because it cannot easily embed two distinct, competing concepts into a single point in the vector space. The `QueryDecomposer` breaks these complex queries into multiple, atomic sub-queries.

## Implementation Details
- **Module:** `src/rag/query/decomposer.py`
- **LLM Integration:** Uses `ChatGoogleGenerativeAI` with `with_structured_output(SubQueries)` to forcefully return a strict list of strings.
- **Logic:**
  1. If the query is simple (e.g., "What is the max temp of M04?"), the LLM returns a single-item list.
  2. If the query is comparative, it splits it into distinct, atomic lookups (e.g., `["maintenance schedule for M04", "maintenance schedule for M05"]`).
- **Graceful Fallback:** If the LLM is missing or the API call fails, it safely falls back to returning the raw query inside a single-item list, ensuring downstream retrieval steps continue without interruption.
- **Execution:** Downstream, the RAG agent will iterate over this array, execute the Hybrid Retrieval pipeline for each sub-query, and merge the results into a single candidate pool before passing it to the Reranker.
