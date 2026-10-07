# Metadata-Aware Retrieval

## Overview
Users often include implicit or explicit constraints in their natural language queries (e.g., "maintenance for M04" or "refer to SOP-14"). Relying purely on embedding semantics to isolate these constraints is unreliable. 

The Metadata-Aware Retrieval system intercepts the query before it hits the vector index and translates semantic intent into database filters.

## Components
- **QueryAnalyzer** (`src/rag/query/analyzer.py`):
  Extracts entities using zero-latency regex matching (for strict constraints like Machine IDs and Document IDs) and keyword mapping (for soft prioritization like document types).
- **Strict Filters (`filters`)**:
  Applied directly inside the database engines (ChromaDB `where` clause and sparse attribute matching). Any chunk failing the constraint is instantly eliminated.
- **Soft Prioritization (`soft_filters`)**:
  If the user asks for a "procedure", chunks labeled `document_type=SOP` receive a $+0.5$ RRF score boost during candidate fusion. This pushes preferred formats to the top without blindly censoring valid answers that might reside in a manual.
