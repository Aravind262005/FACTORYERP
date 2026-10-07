# Dense Vector Index

## Overview
The Dense Retriever uses `ChromaDB` as its vector database, wrapping it in the `DenseRetriever` class (`src/rag/retrieval/dense.py`). This satisfies the requirement to maintain the project's existing vector store.

## Implementation Features
- **Embeddings**: Uses `sentence-transformers` via ChromaDB's built-in `DefaultEmbeddingFunction` (`all-MiniLM-L6-v2`) which is lightweight, fast, and requires no external API keys.
- **Duplicate Prevention**: Before indexing chunks, the system checks existing IDs (`chunk_id`) using `collection.get(ids=...)`. Only new chunk IDs are embedded and inserted, preventing duplicate records on re-ingestion.
- **Metadata Flattening**: Pydantic `ChunkMetadata` is serialized to a flat dictionary. Any complex types are cast to strings, as required by ChromaDB.
- **Search Capabilities**: Supports querying with dynamic `top_k` and `filters`. It converts the Chroma distances to inverted similarity scores (e.g. `1.0 - distance`).

## File Cleanup
Because ChromaDB handles persistence via file handles (SQLite), deleting a document calls `collection.delete(where={"document_id": document_id})`. This removes all chunks cleanly without having to explicitly iterate them.
