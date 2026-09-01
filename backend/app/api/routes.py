from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import AgentExecution, ToolExecution, DecisionAudit
from app.graph.workflow import workflow

router = APIRouter()

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    query_id: str
    status: str

# In-memory store for query status (since no specific table was requested for the high-level queries history)
# We will use DecisionAudit for history as it has query_id, final_recommendation, status, created_at.
active_queries: Dict[str, Dict[str, Any]] = {}

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
                duration_ms=100 # Mock duration
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
    # In reality query_id format QRY-YYYY-NNNN
    year = datetime.now().year
    # Mock NNNN with a random 4 digit
    import random
    nnnn = f"{random.randint(1000, 9999)}"
    query_id = f"QRY-{year}-{nnnn}"
    
    active_queries[query_id] = {"status": "processing", "query": req.query}
    
    background_tasks.add_task(run_workflow, query_id, req.query, db)
    return QueryResponse(query_id=query_id, status="processing")

@router.get("/queries/{query_id}")
def get_query(query_id: str):
    if query_id not in active_queries:
        raise HTTPException(status_code=404, detail="Query not found")
    return active_queries[query_id]

@router.get("/queries")
def list_queries(db: Session = Depends(get_db)):
    # Returns paginated query history
    audits = db.query(DecisionAudit).order_by(DecisionAudit.created_at.desc()).limit(50).all()
    res = []
    for a in audits:
        res.append({
            "query_id": a.query_id,
            "status": a.status,
            "confidence": a.confidence,
            "recommendation": a.final_recommendation,
            "date": a.created_at.isoformat()
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
