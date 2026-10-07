import re
from typing import Dict, Any, Tuple

class QueryAnalyzer:
    """Analyzes a user query to extract strict filters and soft prioritization hints."""
    
    def __init__(self):
        # Known document types mapping
        self.doc_types = {
            "sop": "SOP",
            "procedure": "SOP",
            "manual": "MANUAL",
            "guide": "MANUAL",
            "policy": "POLICY",
            "safety": "SAFETY POLICY"
        }
        
    def analyze(self, query: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Returns:
            strict_filters (Dict): Constraints that MUST be met.
            soft_filters (Dict): Constraints that SHOULD be prioritized.
        """
        strict_filters = {}
        soft_filters = {}
        
        query_lower = query.lower()
        
        # 1. Extract Machine IDs (e.g. M01, M04)
        machine_match = re.search(r'\b(m\d{2,3})\b', query_lower)
        if machine_match:
            # We use strict filter if the user explicitly asks about a machine
            strict_filters["machine_id"] = machine_match.group(1).upper()
            
        # 2. Extract Document ID (e.g. SOP-14)
        doc_id_match = re.search(r'\b([a-z]+-\d+)\b', query_lower)
        if doc_id_match:
            strict_filters["document_id"] = doc_id_match.group(1).upper()
            
        # 3. Extract Document Type (Soft Prioritization)
        # If a user says "What is the procedure...", they probably want an SOP, 
        # but a manual might also answer it. So we soft-filter.
        for kw, dt in self.doc_types.items():
            if kw in query_lower:
                soft_filters["document_type"] = dt
                break
                
        # 4. Check for Historical/Superseded Intent
        historical_kws = ["previous", "old", "superseded", "deprecated", "past", "history"]
        if any(kw in query_lower for kw in historical_kws):
            # If they want historical docs, we don't enforce 'current'
            strict_filters["historical_intent"] = True
            
        return strict_filters, soft_filters
