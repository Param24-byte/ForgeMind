# pyrefly: ignore [missing-import]
from fastapi import FastAPI
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os

# Add paths to sys for importing Orchestrator and Ingestion
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'agents'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ingestion'))

from orchestrator import AgentOrchestrator
from ingestion_pipeline import IngestionPipeline

app = FastAPI(title="Unified Operations Brain API")

# Enable CORS for the Next.js frontend (localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = AgentOrchestrator()
pipeline = IngestionPipeline()

# Global state to mock pending HITL work orders
pending_approvals = {
    "WO-DEMO-001": {
        "id": "WO-DEMO-001",
        "AssetID": "P-102",
        "Priority": "CRITICAL",
        "OrderType": "PM01",
        "Description": "Inspect and Realign Drive End Bearing",
        "GeneratedBy": "RCA Agent Swarm"
    }
}

class QueryRequest(BaseModel):
    query: str

@app.get("/api/health")
def health_check():
    return {"status": "System Online", "version": "1.0.0"}

@app.post("/api/ingest")
def trigger_ingestion():
    result = pipeline.run_ingestion()
    return result

@app.post("/api/query")
def process_query(req: QueryRequest):
    result = orchestrator.process_query(req.query)
    
    # If the RCA agent drafted a WO, add it to pending approvals
    if result.get("draft_work_order"):
        wo_id = f"WO-GEN-{len(pending_approvals) + 1:03d}"
        draft = result["draft_work_order"].get("body", {})
        pending_approvals[wo_id] = {
            "id": wo_id,
            "AssetID": draft.get("AssetID", "Unknown"),
            "Priority": draft.get("Priority", "MEDIUM"),
            "OrderType": draft.get("OrderType", "PM01"),
            "Description": draft.get("Description", "AI Generated Work Order"),
            "GeneratedBy": result.get("agent_name", "AI System")
        }
        
    return result

@app.get("/api/approvals")
def get_approvals():
    return {"pending_approvals": list(pending_approvals.values())}

@app.post("/api/approvals/{wo_id}/approve")
def approve_wo(wo_id: str):
    if wo_id in pending_approvals:
        del pending_approvals[wo_id]
        return {"success": True, "message": f"Work Order {wo_id} sent to SAP (simulated)."}
    return {"success": False, "message": "Work order not found."}

@app.post("/api/approvals/{wo_id}/reject")
def reject_wo(wo_id: str):
    if wo_id in pending_approvals:
        del pending_approvals[wo_id]
        return {"success": True, "message": f"Status rejected. Knowledge evolution triggered in Graph DB for {wo_id}."}
    return {"success": False, "message": "Work order not found."}
