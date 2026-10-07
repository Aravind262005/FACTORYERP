# RAG Decisions Log

This document tracks all major architectural and implementation decisions for the Manufacturing Policy-Aware Hybrid Hierarchical RAG.

## Phase 0 Decisions
- **Decision:** Build RAG pipeline as a decoupled module in `src/rag/` first.
- **Reason:** To avoid disrupting the existing functioning `KnowledgeAgent` and LangGraph workflow while building and testing complex sub-components.
- **Decision:** Retain ChromaDB as the vector database.
- **Reason:** It is the current vector database used in the `KnowledgeAgent`, satisfying the requirement not to blindly replace existing technologies unless necessary.
