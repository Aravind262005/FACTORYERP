import os
import logging
from typing import Dict, Any

from src.rag.query.analyzer import QueryAnalyzer
from src.rag.query.rewriter import QueryRewriter
from src.rag.query.decomposer import QueryDecomposer
from src.rag.retrieval.dense import DenseRetriever
from src.rag.retrieval.sparse import SparseRetriever
from src.rag.retrieval.hybrid import HybridRetriever
from src.rag.retrieval.reranker import Reranker
from src.rag.retrieval.context_builder import ContextBuilder
from src.rag.evidence import EvidencePackager
from src.rag.generation import AnswerGenerator

logger = logging.getLogger(__name__)

class KnowledgeAgent:
    """
    The main RAG Knowledge Agent that orchestrates the entire retrieval pipeline.
    This replaces the legacy stub and integrates cleanly with the LangGraph workflow.
    """
    def __init__(self, db_path="./chroma_db", llm=None):
        self.db_path = db_path
        
        # 1. Query Processing
        self.analyzer = QueryAnalyzer()
        self.rewriter = QueryRewriter(llm=llm)
        self.decomposer = QueryDecomposer(llm=llm)
        
        # 2. Retrieval
        self.dense = DenseRetriever(db_path=self.db_path)
        self.sparse = SparseRetriever()
        # In a real environment, sparse needs to be loaded/indexed continuously.
        # For this integration, we assume it's synced with dense or populated externally.
        self.hybrid = HybridRetriever(self.dense, self.sparse)
        
        # 3. Post-Processing
        self.reranker = Reranker()
        self.context_builder = ContextBuilder(self.dense)
        self.packager = EvidencePackager()
        
        # 4. Generation
        self.generator = AnswerGenerator(llm=llm)

    def index_chunks(self, chunks: list):
        """
        Helper method to populate the retrievers with new chunks.
        """
        self.dense.index_chunks(chunks)
        self.sparse.index_chunks(chunks)

    def execute(self, query: str) -> Dict[str, Any]:
        """
        Executes the full RAG pipeline.
        Signature matches exactly what LangGraph expects.
        """
        try:
            # 1. Analyze metadata constraints
            strict_filters, soft_filters = self.analyzer.analyze(query)
            
            # 2. Decompose into atomic sub-queries (handles multi-hop)
            sub_queries = self.decomposer.decompose(query)
            
            # 3. Process each sub-query
            all_candidates = []
            seen_cids = set()
            
            for sq in sub_queries:
                # 3a. Rewrite for optimal retrieval
                optimized_sq = self.rewriter.rewrite(sq)
                
                # 3b. Hybrid Retrieval
                results = self.hybrid.search(
                    query=optimized_sq,
                    top_k=5, 
                    filters=strict_filters,
                    soft_filters=soft_filters
                )
                
                # Deduplicate across sub-queries
                for r in results:
                    cid = r["chunk_id"]
                    if cid not in seen_cids:
                        all_candidates.append(r)
                        seen_cids.add(cid)
                        
            # 4. Post-Retrieval Reranking
            reranked = self.reranker.rerank(query, all_candidates, top_k=5)
            
            # 5. Parent Context Expansion
            expanded_context = self.context_builder.expand_context(reranked)
            
            # 6. Evidence Packaging
            evidence_str = self.packager.package(expanded_context)
            
            # 7. Grounded Generation
            final_result = self.generator.generate(query, evidence_str)
            final_result["status"] = "success"
            
            return final_result
            
        except Exception as e:
            print(f"KnowledgeAgent Error: {e}")
            logger.error(f"KnowledgeAgent execution failed: {str(e)}")
            return {
                "status": "error",
                "answer": f"KnowledgeAgent execution failed: {str(e)}",
                "sources": [],
                "confidence": 0.0
            }
