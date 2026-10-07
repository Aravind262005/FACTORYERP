# Knowledge Agent Integration

## Overview
The individual phases (Chunking, Retrieval, Query Processing, Generation) have been unified into the final `KnowledgeAgent` (`backend/app/agents/knowledge/agent.py`). This class replaces the original dummy stub and acts as the official RAG node in the multi-agent LangGraph workflow.

## Architecture Pipeline
When `agent.execute(query)` is called by LangGraph, the following synchronous pipeline is executed:

1. **Query Analyzer**: Extracts strict metadata constraints (`machine_id`, `authority_level`) and soft prioritization hints (`document_type`).
2. **Query Decomposer**: Analyzes if the query is multi-hop/comparative. If so, it splits it into an array of atomic sub-queries.
3. **Query Rewriter**: Iterates over the sub-queries, using the LLM to expand acronyms, fix typos, and strip conversational filler.
4. **Hybrid Retriever**: Executes a combined Dense (ChromaDB) and Sparse (BM25) search for each sub-query, fusing the candidates via Reciprocal Rank Fusion (RRF).
5. **Reranker**: Passes the deduplicated candidate pool through a CrossEncoder (`ms-marco-MiniLM-L-6-v2`) to achieve perfect pairwise relevance sorting.
6. **Context Builder**: Detects if any retrieved chunk is a child fragment (e.g., a table row) and seamlessly swaps it with its parent section to provide surrounding context.
7. **Evidence Packager**: Wraps the final chunks in strict citation boundary markers `[Source: DocID | Page X]`.
8. **Answer Generator**: Uses the LLM (`gemini-2.5-flash`) to generate the final response, strictly adhering to the `INSUFFICIENT_EVIDENCE` fallback rule.

## Interface Compatibility
The method strictly returns `{"status": str, "answer": str, "sources": list, "confidence": float}`, ensuring 100% compatibility with the existing Planner, Critic, and LangGraph state schemas.
