# Parent Context Expansion

## Overview
When a RAG system retrieves small child chunks (e.g., a single table row or a single bullet point warning), the LLM often lacks the surrounding context to generate a confident answer. The `ContextBuilder` solves this by replacing highly ranked child chunks with their original parent section.

## Implementation Details
- **Module:** `src/rag/retrieval/context_builder.py`
- **Logic Flow:**
  1. Receives the final reranked list of chunk candidates.
  2. Iterates over the candidates and identifies any chunk containing a `parent_id` in its metadata.
  3. Batches these `parent_id`s and performs a single `$in` query to the Dense Retriever (ChromaDB) to fetch the full text of the parent section.
  4. Swaps the child chunk in the results list with the parent chunk.
- **Deduplication:**
  If multiple child chunks belonging to the *same* parent are retrieved (e.g., Row 1 and Row 2 of the same table), the `ContextBuilder` intelligently merges them. It inserts the parent chunk only once and discards the redundant child chunks. This prevents blowing up the LLM context window with duplicated parent text.
- **Graceful Fallback:**
  If a parent chunk cannot be found in the database for any reason, the system safely retains the original child chunk in the final context list.
