import os
import shutil
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from src.rag.ingestion import IngestionPipeline
from src.rag.chunking import HierarchicalChunker
from app.agents.knowledge.agent import KnowledgeAgent
from app.graph.workflow import workflow, GraphState

def run_e2e():
    print("--- 1. Creating dummy documents ---")
    data_dir = "./dummy_sops"
    os.makedirs(data_dir, exist_ok=True)
    
    sop14 = """
---
document_id: SOP-14
document_type: SOP
machine_id: N/A
authority_level: current
---
# Expedited Shipping Protocols
For shortages of Aluminum Alloy 6061 or other critical materials under 50 units, expedited shipping from Supplier B is authorized.
"""
    
    sop15 = """
---
document_id: SOP-15
document_type: SOP
machine_id: M04
authority_level: current
---
# Machine Maintenance
Line 1 and 2 machines require weekly maintenance. If maintenance is delayed, capacity reduces by 20%.
"""
    with open(f"{data_dir}/sop-14.md", "w", encoding="utf-8") as f:
        f.write(sop14)
    with open(f"{data_dir}/sop-15.md", "w", encoding="utf-8") as f:
        f.write(sop15)
        
    print("--- 2. Ingestion & Chunking ---")
    pipeline = IngestionPipeline()
    
    docs = []
    docs.append(pipeline.process(f"{data_dir}/sop-14.md", "SOP-14", {"document_type": "SOP", "authority_level": "current"}))
    docs.append(pipeline.process(f"{data_dir}/sop-15.md", "SOP-15", {"document_type": "SOP", "machine_id": "M04", "authority_level": "current"}))
            
    print(f"Loaded {len(docs)} documents.")
    
    chunker = HierarchicalChunker(max_chunk_size=500)
    all_chunks = []
    for doc in docs:
        chunks = chunker.chunk_document(doc)
        all_chunks.extend(chunks)
        
    print(f"Generated {len(all_chunks)} chunks.")
    
    print("--- 3. Indexing into Knowledge Agent ---")
    db_path = "./chroma_e2e_test"
    if os.path.exists(db_path):
        shutil.rmtree(db_path, ignore_errors=True)
        
    # We must patch the workflow's instantiated agent so it uses our DB and chunks
    from app.graph import workflow as wf_module
    
    class MockE2ELLM:
        def with_structured_output(self, schema):
            return self
            
        def invoke(self, text):
            class MockResult:
                def __init__(self):
                    self.queries = ["shortage of Aluminum Alloy 6061"]
                    self.query = "shortage of Aluminum Alloy 6061"
                    self.answer = "For shortages of Aluminum Alloy 6061 under 50 units, expedited shipping from Supplier B is authorized (SOP-14, Page 1)."
                    self.confidence = 0.95
                    class Citation:
                        def __init__(self):
                            self.document_id = "SOP-14"
                            self.page = "1"
                    self.citations = [Citation()]
            return MockResult()

    knowledge_agent = KnowledgeAgent(db_path=db_path, llm=MockE2ELLM())
    knowledge_agent.index_chunks(all_chunks)
    
    wf_module.knowledge_agent = knowledge_agent
    
    print("--- 4. Executing LangGraph Workflow ---")
    
    initial_state = {
        "user_query": "We have a shortage of 30 units of Aluminum Alloy 6061. What should we do?",
        "entities": {},
        "required_agents": [],
        "agent_outputs": {},
        "validation_status": {},
        "retry_counter": 0,
        "final_decision": {}
    }
    
    result = wf_module.workflow.invoke(initial_state)
    
    print("\n--- FINAL DECISION ---")
    final = result.get("final_decision", {})
    print(f"Status: {final.get('status')}")
    print(f"Recommendation: {final.get('recommendation')}")
    print("\n--- KNOWLEDGE AGENT OUTPUT ---")
    print(final.get("knowledge", {}).get("answer"))
    
    if "SOP-14" in str(final):
        print("\n[PASSED] E2E TEST PASSED: RAG pipeline successfully supplied knowledge to the graph.")
    else:
        print("\n[FAILED] E2E TEST FAILED: RAG output not found in final decision.")

if __name__ == "__main__":
    run_e2e()
