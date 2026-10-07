import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from typing import List, Dict, Any, Optional
from ..schema import ChunkMetadata
import json

class DenseRetriever:
    def __init__(self, db_path: str = "./chroma_db", collection_name: str = "manufacturing_kb"):
        self.client = chromadb.PersistentClient(path=db_path)
        # Using the default sentence-transformers model that chromadb ships with (all-MiniLM-L6-v2)
        # It's fast and suitable for the baseline.
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn,
            metadata={"description": "Dense vector index for manufacturing documents"}
        )

    def _prepare_metadata(self, chunk: ChunkMetadata) -> Dict[str, Any]:
        """Flattens chunk metadata for ChromaDB which only accepts str, int, float, bool."""
        metadata = chunk.model_dump(exclude_none=True)
        # Ensure complex types are strings if any slip through (e.g., datetime)
        for k, v in metadata.items():
            if not isinstance(v, (str, int, float, bool)):
                metadata[k] = str(v)
        return metadata

    def index_chunks(self, chunks: List[ChunkMetadata]) -> Dict[str, int]:
        """Indexes a list of chunks, preventing duplicates via chunk_id."""
        if not chunks:
            return {"added": 0, "updated": 0, "ignored": 0}
            
        ids = [c.chunk_id for c in chunks]
        texts = [c.text for c in chunks]
        metadatas = [self._prepare_metadata(c) for c in chunks]
        
        # Check existing to prevent duplicate embeddings
        existing = self.collection.get(ids=ids, include=[])
        existing_ids = set(existing["ids"])
        
        new_ids, new_texts, new_metadatas = [], [], []
        
        for i, cid in enumerate(ids):
            if cid not in existing_ids:
                new_ids.append(cid)
                new_texts.append(texts[i])
                new_metadatas.append(metadatas[i])
                
        if new_ids:
            self.collection.add(
                ids=new_ids,
                documents=new_texts,
                metadatas=new_metadatas
            )
            
        return {"added": len(new_ids), "updated": 0, "ignored": len(ids) - len(new_ids)}

    def delete_document(self, document_id: str):
        """Deletes all chunks associated with a document_id."""
        self.collection.delete(where={"document_id": document_id})

    def search(self, query: str, top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Performs a dense similarity search."""
        
        kwargs = {
            "query_texts": [query],
            "n_results": top_k,
            "include": ["metadatas", "documents", "distances"]
        }
        
        if filters:
            if len(filters) == 1:
                kwargs["where"] = filters
            else:
                kwargs["where"] = {"$and": [{k: v} for k, v in filters.items()]}
            
        results = self.collection.query(**kwargs)
        
        output = []
        if not results["ids"] or not results["ids"][0]:
            return output
            
        for idx, chunk_id in enumerate(results["ids"][0]):
            output.append({
                "chunk_id": chunk_id,
                "text": results["documents"][0][idx],
                "score": 1.0 - results["distances"][0][idx], # Simple distance to similarity inversion
                "metadata": results["metadatas"][0][idx]
            })
            
        return output
