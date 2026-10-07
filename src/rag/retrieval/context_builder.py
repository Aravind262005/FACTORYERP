from typing import List, Dict, Any, Set
from .dense import DenseRetriever

class ContextBuilder:
    def __init__(self, dense_retriever: DenseRetriever):
        self.dense = dense_retriever

    def expand_context(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Expands child chunks into their parent context.
        Consolidates adjacent children under the same parent to avoid context duplication.
        """
        if not candidates:
            return []
            
        parent_ids_to_fetch = set()
        standalone_chunks = []
        
        # 1. Identify which chunks need parent expansion
        for cand in candidates:
            metadata = cand.get("metadata", {})
            parent_id = metadata.get("parent_id")
            
            if parent_id:
                parent_ids_to_fetch.add(parent_id)
            else:
                # It's already a parent chunk or has no parent
                standalone_chunks.append(cand)
                
        # 2. Fetch all required parent chunks from the dense store (ChromaDB)
        fetched_parents = {}
        if parent_ids_to_fetch:
            # ChromaDB get by IDs
            result = self.dense.collection.get(
                ids=list(parent_ids_to_fetch),
                include=["metadatas", "documents"]
            )
            
            if result and result["ids"]:
                for idx, pid in enumerate(result["ids"]):
                    fetched_parents[pid] = {
                        "chunk_id": pid,
                        "text": result["documents"][idx],
                        "metadata": result["metadatas"][idx],
                        "expanded": True
                    }
                    
        # 3. Reconstruct the final list
        final_context = []
        seen_parents = set()
        
        for cand in candidates:
            metadata = cand.get("metadata", {})
            parent_id = metadata.get("parent_id")
            
            if parent_id:
                if parent_id in fetched_parents and parent_id not in seen_parents:
                    # We swap the child for the full parent
                    final_context.append(fetched_parents[parent_id])
                    seen_parents.add(parent_id)
                elif parent_id not in fetched_parents and cand["chunk_id"] not in seen_parents:
                    # Fallback: if parent not found for some reason, keep child
                    final_context.append(cand)
                    seen_parents.add(cand["chunk_id"])
            else:
                if cand["chunk_id"] not in seen_parents:
                    final_context.append(cand)
                    seen_parents.add(cand["chunk_id"])
                    
        return final_context
