import sys
import os
# Ensure project root is in sys.path before any local imports that depend on src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import AgentExecution, ToolExecution, DecisionAudit
from app.graph.workflow import workflow

# We need to import the RAG pipeline components
# We must ensure they can be imported
from src.rag.ingestion import IngestionPipeline
from src.rag.chunking import HierarchicalChunker
from app.agents.knowledge.agent import KnowledgeAgent
from fastapi import UploadFile, File, Form

# Initialize global knowledge agent and pipeline
# Using the same db_path as the E2E test to avoid conflict, or a default one
knowledge_db_path = "./chroma_api_db"
knowledge_agent_instance = KnowledgeAgent(db_path=knowledge_db_path)
ingestion_pipeline = IngestionPipeline()
chunker = HierarchicalChunker(max_chunk_size=500)

uploaded_documents_store = []

router = APIRouter()

class KnowledgeQueryRequest(BaseModel):
    query: str

@router.post("/knowledge/upload")
async def upload_document(file: UploadFile = File(...), document_type: str = Form("SOP")):
    temp_path = f"./temp_{file.filename}"
    try:
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
            
        doc_id = file.filename.split('.')[0]
        metadata = {"document_type": document_type, "filename": file.filename}
        
        doc = ingestion_pipeline.process(temp_path, doc_id, metadata)
        chunks = chunker.chunk_document(doc)
        knowledge_agent_instance.index_chunks(chunks)
        
        doc_info = {
            "id": doc_id,
            "filename": file.filename,
            "document_type": document_type,
            "upload_date": datetime.now().isoformat(),
            "status": "Indexed",
            "chunks": len(chunks)
        }
        uploaded_documents_store.append(doc_info)
        
        return {"status": "success", "document": doc_info}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Server error: {str(e)}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@router.get("/knowledge/documents")
def list_documents():
    return {"documents": uploaded_documents_store}

@router.delete("/knowledge/documents/{doc_id}")
def delete_document(doc_id: str):
    global uploaded_documents_store
    
    # Remove from store
    found = False
    for i, doc in enumerate(uploaded_documents_store):
        if doc["id"] == doc_id:
            uploaded_documents_store.pop(i)
            found = True
            break
            
    if not found:
        raise HTTPException(status_code=404, detail="Document not found")
        
    # Remove from ChromaDB (dense)
    try:
        knowledge_agent_instance.dense.delete_document(doc_id)
        # For sparse (in-memory BM25), we rebuild it from remaining chunks
        new_chunks = [c for c in knowledge_agent_instance.sparse.chunks if getattr(c, "document_id", None) != doc_id]
        knowledge_agent_instance.sparse.index_chunks(new_chunks)
    except Exception as e:
        # Just log or ignore if delete fails partially
        pass
        
    return {"status": "success", "message": "Document deleted successfully"}

query_history_store = []

@router.post("/knowledge/query")
def query_knowledge(req: KnowledgeQueryRequest, db: Session = Depends(get_db)):
    try:
        result = knowledge_agent_instance.execute(req.query)
        
        import uuid
        from datetime import datetime
        query_id = f"QRY-{datetime.now().year}-{str(uuid.uuid4())[:4].upper()}"
        
        # Save to DB
        audit = DecisionAudit(
            query_id=query_id,
            final_recommendation=result.get("answer", "")[:60] + "...",
            confidence=result.get("confidence", 0),
            status="Resolved" if result.get("answer") and result.get("answer") != "INSUFFICIENT_EVIDENCE" else "Unresolved"
        )
        db.add(audit)
        
        exec_log = AgentExecution(
            query_id=query_id,
            agent_name="Knowledge Agent",
            input=req.query,
            output="Processed via Knowledge Agent",
            duration_ms=100
        )
        db.add(exec_log)
        db.commit()
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    query_id: str
    status: str

active_queries: Dict[str, Dict[str, Any]] = {}

class HistoryEntryRequest(BaseModel):
    query: str
    status: str
    confidence: int

@router.post("/history")
def add_to_history(req: HistoryEntryRequest, db: Session = Depends(get_db)):
    import uuid
    from datetime import datetime
    year = datetime.now().year
    query_id = f"QRY-{year}-{str(uuid.uuid4())[:4].upper()}"
    
    # Save to DecisionAudit
    audit = DecisionAudit(
        query_id=query_id,
        final_recommendation="Approved and proceeded via workflow.",
        confidence=float(req.confidence) / 100.0,
        status=req.status
    )
    db.add(audit)
    
    # Save a mock AgentExecution so it shows the input query and agents
    for agent in ["Planner", "Production", "Inventory", "Critic"]:
        exec_log = AgentExecution(
            query_id=query_id,
            agent_name=agent,
            input=req.query,
            output="Mock execution for history",
            duration_ms=100
        )
        db.add(exec_log)
    
    db.commit()
    return {"status": "success", "id": query_id}

@router.post("/auth/login")
def login():
    return {"access_token": "mock-jwt-token", "token_type": "bearer"}

def run_workflow(query_id: str, query: str, db: Session):
    try:
        # Initial state
        state = {
            "user_query": query,
            "entities": {},
            "required_agents": [],
            "agent_outputs": {},
            "validation_status": {},
            "retry_counter": 0,
            "final_decision": {}
        }
        
        # Run graph
        result = workflow.invoke(state)
        final = result.get("final_decision", {})
        
        # Save to active_queries
        active_queries[query_id] = {
            "status": final.get("status", "resolved"),
            "result": final
        }
        
        # Log to DecisionAudit
        audit = DecisionAudit(
            query_id=query_id,
            final_recommendation=final.get("recommendation"),
            confidence=final.get("confidence", 0.0),
            status=final.get("status", "resolved")
        )
        db.add(audit)
        
        # Log agent executions
        for agent_name, output in result.get("agent_outputs", {}).items():
            exec_log = AgentExecution(
                query_id=query_id,
                agent_name=agent_name,
                input=query,
                output=str(output),
                duration_ms=100
            )
            db.add(exec_log)
            
        db.commit()
    except Exception as e:
        active_queries[query_id] = {
            "status": "error",
            "result": {"error": str(e)}
        }

@router.post("/queries", response_model=QueryResponse)
def create_query(req: QueryRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    import random
    year = datetime.now().year
    nnnn = f"{random.randint(1000, 9999)}"
    query_id = f"QRY-{year}-{nnnn}"
    
    active_queries[query_id] = {"status": "processing", "query": req.query}
    
    # Run the real workflow in DB if requested
    background_tasks.add_task(run_workflow, query_id, req.query, db)
    
    return QueryResponse(query_id=query_id, status="processing")

@router.get("/queries/{query_id}")
def get_query(query_id: str):
    if query_id not in active_queries:
        raise HTTPException(status_code=404, detail="Query not found")
    return active_queries[query_id]

@router.get("/queries")
def list_queries(db: Session = Depends(get_db)):
    audits = db.query(DecisionAudit).order_by(DecisionAudit.created_at.desc()).limit(50).all()
    res = []
    for a in audits:
        first_exec = db.query(AgentExecution).filter(AgentExecution.query_id == a.query_id).first()
        title = first_exec.input if first_exec and first_exec.input else "Unknown Query"
        
        agents = [e[0] for e in db.query(AgentExecution.agent_name).filter(AgentExecution.query_id == a.query_id).distinct().all()]
        if not agents:
            agents = ["AI"]
            
        dt = a.created_at
        
        res.append({
            "id": a.query_id,
            "title": title[:60] + "..." if len(title) > 60 else title,
            "subtitle": a.final_recommendation[:60] + "..." if a.final_recommendation and len(a.final_recommendation) > 60 else "",
            "date": dt.strftime("%b %d, %Y") if dt else "Unknown",
            "time": dt.strftime("%H:%M:%S") if dt else "Unknown",
            "status": str(a.status).capitalize(),
            "confidence": int(a.confidence * 100) if a.confidence is not None else None,
            "agents": agents,
            "alert": (a.confidence is not None and a.confidence < 0.5)
        })
    return {"queries": res}

@router.get("/audit/{query_id}")
def get_audit_trail(query_id: str, db: Session = Depends(get_db)):
    executions = db.query(AgentExecution).filter(AgentExecution.query_id == query_id).all()
    return {
        "query_id": query_id,
        "agent_executions": [
            {
                "agent_name": e.agent_name,
                "input": e.input,
                "output": e.output,
                "timestamp": e.timestamp.isoformat(),
                "duration_ms": e.duration_ms
            } for e in executions
        ]
    }
