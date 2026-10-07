# Evidence Packaging

## Overview
Retrieving accurate chunks is only half the RAG battle. If the LLM is handed an unformatted, messy string of text, it will struggle to properly synthesize the answer and cite its sources. The `EvidencePackager` formats the final context block to enforce strict adherence to manufacturing guidelines.

## Implementation Details
- **Module:** `src/rag/evidence.py`
- **Formatting:** For every retrieved chunk, it creates an explicit boundary block:
  ```
  --- EVIDENCE ITEM X ---
  [Source: {document_id} | Type: {document_type} | Authority: {authority_level} | Page: {page}]
  {chunk_text}
  ```
- **Why this matters:**
  - **Source Transparency:** The LLM can explicitly see where the text came from, allowing it to generate grounded citations (e.g. "According to SOP-14, page 2...").
  - **Authority Weighting:** Even if a superseded document somehow bypassed the filters, the LLM explicitly sees `Authority: superseded` in the tag, acting as a final line of defense against hallucinations or policy violations.
- **Empty State:** If no chunks are retrieved, it strictly returns `"NO EVIDENCE FOUND."`, which acts as a hard trigger for the LLM to output `INSUFFICIENT_EVIDENCE` as mandated by the core RAG principles.
