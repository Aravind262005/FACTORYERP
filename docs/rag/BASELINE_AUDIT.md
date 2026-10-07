# Baseline Audit Report

## 1. What RAG functionality already exists?
- The current implementation resides in `backend/app/agents/knowledge/agent.py` under the `KnowledgeAgent` class.
- Uses `chromadb.PersistentClient` as the vector database (directory: `./chroma_db`).
- Embeddings are handled implicitly by ChromaDB (which defaults to `all-MiniLM-L6-v2`).
- A `_seed_documents` method seeds exactly two hardcoded mock SOPs.
- Existing metadata structure includes: `document_id`, `page`, `chunk_id`.
- Retrieval uses a simple dense vector search (`self.collection.query` with `n_results=1`).
- The answer generation does not use an LLM for grounding; it uses a synthesized hardcoded fallback.

## 2. What is missing?
- **Data Contract:** Formal schema for documents, parent/child chunks, and extended metadata (version, authority).
- **Document Ingestion:** Proper parsers for PDF/DOCX, layout extraction, table preservation.
- **Hierarchical Chunking:** Linking child chunks to parent context.
- **Hybrid Retrieval:** Sparse (BM25) search alongside dense search.
- **Metadata Filtering:** Hard constraints on machine ID, material, SOP revision.
- **Reranking:** Cross-encoder step to reorder retrieved candidates.
- **Context Expansion:** Fetching parent section of the matched child chunk.
- **Query Processing:** Rewriting and decomposition for multi-faceted questions.
- **Grounded LLM Generation:** Generating answers with traceable citations (preventing hallucinations).
- **Evaluation:** No current test framework or datasets to measure Recall@5.

## 3. Which files will be modified?
- `backend/app/agents/knowledge/agent.py` (Final integration in Phase 15).
- `backend/requirements.txt` (New dependencies for RAG like BM25, parser, reranker).

## 4. Which files should remain untouched?
- Other agents: `PlannerAgent`, `ProductionAgent`, `InventoryProcurementAgent`, `CriticAgent`.
- Core application routing and logic: `app/api/*`, `app/graph/workflow.py`, `app/models/models.py`.
- Frontend code.
- Postgres manufacturing schemas.

## 5. What dependencies already exist?
- `langchain`, `langgraph`, `langchain-google-genai`
- `chromadb`, `transformers`, `torch`, `peft`

## 6. What risks exist?
- Integration into the `KnowledgeAgent` might accidentally change the output format expected by LangGraph and the `CriticAgent`.
- Adding LLM generation in the Knowledge agent increases response latency. Must be carefully measured.
- Complex chunking logic may introduce bugs if document layouts vary unpredictably.

## 7. What is the smallest safe implementation path?
- Develop the RAG pipeline entirely as a standalone Python package (`src/rag/`).
- Build unit tests and integration tests in `evaluation/`.
- Once the pipeline demonstrates high Recall@5 and correct data formatting, integrate it as a backend utility called by `KnowledgeAgent.execute()`.
