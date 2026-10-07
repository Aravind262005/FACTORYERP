from typing import List, Dict, Any

class EvidencePackager:
    def __init__(self):
        pass

    def package(self, chunks: List[Dict[str, Any]]) -> str:
        """
        Compiles retrieved chunks into a standardized evidence string for the LLM.
        Enforces strict citation metadata blocks.
        """
        if not chunks:
            return "NO EVIDENCE FOUND."
            
        evidence_blocks = []
        
        for idx, chunk in enumerate(chunks):
            metadata = chunk.get("metadata", {})
            doc_id = metadata.get("document_id", "UNKNOWN_DOC")
            doc_type = metadata.get("document_type", "UNKNOWN_TYPE")
            authority = metadata.get("authority_level", "UNKNOWN_AUTH")
            page = metadata.get("page", "N/A")
            
            # Construct standard citation header
            citation_header = f"--- EVIDENCE ITEM {idx + 1} ---"
            source_tag = f"[Source: {doc_id} | Type: {doc_type} | Authority: {authority} | Page: {page}]"
            
            text = chunk.get("text", "").strip()
            
            block = f"{citation_header}\n{source_tag}\n{text}\n"
            evidence_blocks.append(block)
            
        return "\n".join(evidence_blocks)
