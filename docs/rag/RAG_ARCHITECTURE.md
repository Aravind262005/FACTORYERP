# RAG Architecture

## Overview
The "Manufacturing Policy-Aware Hybrid Hierarchical RAG" system will serve as the Knowledge Agent for the Agentic Manufacturing Decision Support Platform. 

## Architectural Components

1. **Document Validation:** Validates source files (PDF, DOCX) and checks for duplicates.
2. **Structure-Aware Extraction:** Extracts text and tables, maintaining structural metadata (headings, pages).
3. **Hierarchical Chunking:** Segments documents into Sections (parents) and Subsections/Paragraphs (children) maintaining `parent_id` relationships.
4. **Embeddings:** Generates dense vector representations of chunks using a configurable embedding model.
5. **Dual Indexing:** Stores chunks in both a dense vector store (ChromaDB) and a sparse lexical index (BM25).
6. **Hybrid Retrieval:** Merges candidates from both dense and sparse searches based on a configurable weighting strategy.
7. **Metadata Filtering:** Hard and soft filters for exact matches (e.g., machine ID, revision, department).
8. **Reranking:** Second-stage cross-encoder to refine top-K retrieved candidates.
9. **Parent Context Expansion:** Retrieves parent sections of highly ranked child chunks to provide sufficient context.
10. **Query Rewriting/Decomposition:** Transforms user queries into manufacturing-specific explicit queries.
11. **Grounded LLM Generation:** Final response synthesis ensuring strict adherence to retrieved evidence without hallucination.

## Data Flow
FACTS → RETRIEVAL → EVIDENCE → REASONING → CITATION
