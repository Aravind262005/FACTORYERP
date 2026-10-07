# Query Rewriting

## Overview
Raw user queries are often sub-optimal for dense and sparse retrieval. Users include conversational filler (e.g., "Hey, what is..."), abbreviations (e.g., "PM"), and typos. The `QueryRewriter` uses the project's LLM (`gemini-2.5-flash`) to transform the raw query into a highly optimized search string before it hits the retrieval pipeline.

## Implementation Details
- **Module:** `src/rag/query/rewriter.py`
- **LLM Integration:** Utilizes `ChatGoogleGenerativeAI` to rewrite queries. 
- **Structured Output:** Uses `with_structured_output(RewrittenQuery)` to strictly enforce that the LLM returns only the final query string, preventing it from generating conversational responses like "Here is the rewritten query: ...".
- **Rules applied by the Prompt:**
  1. Fix spelling mistakes.
  2. Expand manufacturing acronyms (e.g. 'PM' -> 'Preventive Maintenance').
  3. Strip conversational filler.
  4. Preserve critical identifiers (M04, SOP-14).
- **Graceful Fallback:** If the LLM is unavailable or the `GOOGLE_API_KEY` is missing in the environment, the `QueryRewriter` catches the exception and gracefully returns the original raw query. This ensures the RAG pipeline continues functioning (albeit slightly less accurately) rather than crashing entirely.
