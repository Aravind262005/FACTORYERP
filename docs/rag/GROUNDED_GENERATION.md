# Grounded Answer Generation

## Overview
The final step in the internal RAG pipeline is utilizing the LLM to generate a synthesized, highly grounded answer based exclusively on the packaged evidence.

## Implementation Details
- **Module:** `src/rag/generation.py`
- **LLM Integration:** Uses `gemini-2.5-flash` with a strict prompt and `with_structured_output` (enforcing a Pydantic `GroundedAnswer` schema).
- **Core Rules Enforced:**
  1. No hallucination.
  2. Output exactly `"INSUFFICIENT_EVIDENCE"` if the evidence does not answer the query.
  3. Include inline citations matching the `(DocID, Page X)` format from the evidence tags.
- **Null Fast-Path:** If the `EvidencePackager` returns `NO EVIDENCE FOUND.` (e.g., retrieval found nothing), the `AnswerGenerator` immediately short-circuits and returns `INSUFFICIENT_EVIDENCE` without making an API call, saving latency and compute costs.
- **Interface Compatibility:** The output is mapped into the `{"answer": str, "confidence": float, "sources": list}` dictionary format required by the LangGraph multi-agent orchestrator.
