from typing import List, Dict, Any
import logging

try:
    from sentence_transformers import CrossEncoder
    HAS_CROSS_ENCODER = True
except ImportError:
    HAS_CROSS_ENCODER = False

logger = logging.getLogger(__name__)

class Reranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """
        Initializes the CrossEncoder reranker.
        """
        self.model_name = model_name
        self.model = None
        if HAS_CROSS_ENCODER:
            # Lazy loading to avoid blocking startup if unused
            pass

    def _load_model(self):
        if self.model is None and HAS_CROSS_ENCODER:
            try:
                self.model = CrossEncoder(self.model_name)
            except Exception as e:
                logger.warning(f"Failed to load CrossEncoder {self.model_name}: {e}")
                self.model = None

    def rerank(self, query: str, candidates: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Re-scores the candidates against the query using a CrossEncoder.
        Returns the top_k reranked candidates.
        """
        if not candidates:
            return []
            
        self._load_model()
        
        # If model failed to load or package missing, just return the original sorted list
        if self.model is None:
            return candidates[:top_k]

        # Prepare pairs: (Query, Chunk Text)
        pairs = [[query, c["text"]] for c in candidates]
        
        # Predict scores
        scores = self.model.predict(pairs)
        
        # Attach scores and sort
        for i, candidate in enumerate(candidates):
            candidate["cross_encoder_score"] = float(scores[i])
            
        # Sort descending by cross encoder score
        reranked = sorted(candidates, key=lambda x: x["cross_encoder_score"], reverse=True)
        
        return reranked[:top_k]
