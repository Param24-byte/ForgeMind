from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# ==========================================
# NEO4J GRAPH ONTOLOGY (Nodes & Edges)
# ==========================================

class AssetNode(BaseModel):
    """Represents a physical piece of equipment (e.g., Pump, Valve)."""
    asset_id: str = Field(..., description="Unique identifier like P-102")
    name: str
    type: str = Field(..., description="Asset classification (e.g., Centrifugal Pump)")
    location: str
    manufacturer: Optional[str]
    # Edges:
    # - (Asset)-[:HAS_COMPONENT]->(Asset)
    # - (Asset)-[:MAINTAINED_BY]->(Personnel)
    # - (Asset)-[:DOCUMENTED_IN]->(Document)

class DocumentNode(BaseModel):
    """Represents an industrial document (SOP, P&ID, Manual)."""
    doc_id: str
    title: str
    doc_type: str = Field(..., description="SOP, P&ID, Incident Report")
    last_updated: datetime
    version: str
    # Edges:
    # - (Document)-[:REGULATES]->(Asset)
    # - (Document)-[:REFERENCES]->(Document)

class MaintenanceEventNode(BaseModel):
    """Represents a discrete maintenance action from SAP/CMMS."""
    event_id: str
    work_order_id: str
    date: datetime
    issue_description: str
    resolution: str
    # Edges:
    # - (MaintenanceEvent)-[:OCCURRED_ON]->(Asset)
    # - (MaintenanceEvent)-[:RESOLVED_BY]->(Personnel)

class PersonnelNode(BaseModel):
    """Represents an employee, operator, or technician."""
    employee_id: str
    name: str
    role: str
    certification_level: str

# ==========================================
# MILVUS VECTOR STORE SCHEMA (Semantic Chunks)
# ==========================================

class SemanticChunk(BaseModel):
    """Represents a vectorizable chunk of text from a document."""
    chunk_id: str
    doc_id: str = Field(..., description="Foreign key to DocumentNode")
    content: str = Field(..., description="The actual text or parsed table/P&ID data")
    embedding: List[float] = Field(..., description="Vector representation (e.g., 1536 dims)")
    page_number: Optional[int]
    bounding_box: Optional[List[float]] = Field(None, description="[x1, y1, x2, y2] for UI highlighting")

# ==========================================
# GRAPH RELATIONSHIP TYPES
# ==========================================
RELATIONSHIPS = [
    "HAS_COMPONENT",    # P-102 HAS_COMPONENT Valve-V1
    "MAINTAINED_BY",    # P-102 MAINTAINED_BY John Doe
    "DOCUMENTED_IN",    # P-102 DOCUMENTED_IN Pump_Manual_v2
    "OCCURRED_ON",      # Event-992 OCCURRED_ON P-102
    "SUPERSEDES",       # SOP_v2 SUPERSEDES SOP_v1
    "AFFECTS_SYSTEM"    # Valve-V1 AFFECTS_SYSTEM Cooling_Loop_A
]
