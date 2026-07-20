import json
from datetime import datetime
try:
    from .schema import AssetNode, DocumentNode, MaintenanceEventNode, PersonnelNode
except ImportError:
    from schema import AssetNode, DocumentNode, MaintenanceEventNode, PersonnelNode

def generate_mock_data():
    # 1. Assets (Equipment)
    pump = AssetNode(
        asset_id="P-102",
        name="Main Cooling Water Pump",
        type="Centrifugal Pump",
        location="Cooling Unit B",
        manufacturer="Flowserve"
    )
    valve = AssetNode(
        asset_id="V-991",
        name="Discharge Control Valve",
        type="Control Valve",
        location="Cooling Unit B",
        manufacturer="Emerson"
    )

    # 2. Documents (SOPs & Manuals)
    sop_pump = DocumentNode(
        doc_id="DOC-SOP-102",
        title="Centrifugal Pump P-102 Standard Operating Procedure",
        doc_type="SOP",
        last_updated=datetime(2025, 1, 15),
        version="v2.1"
    )
    manual_valve = DocumentNode(
        doc_id="DOC-MAN-991",
        title="Emerson Control Valve Maintenance Manual",
        doc_type="Manual",
        last_updated=datetime(2023, 6, 10),
        version="v1.0"
    )

    # 3. Personnel
    tech_john = PersonnelNode(
        employee_id="EMP-4421",
        name="John Doe",
        role="Senior Maintenance Technician",
        certification_level="Level 3 - Hydraulics"
    )

    # 4. Maintenance Events (History from SAP)
    event_1 = MaintenanceEventNode(
        event_id="EVT-2026-001",
        work_order_id="WO-88123",
        date=datetime(2026, 5, 10),
        issue_description="High vibration detected on P-102 bearing.",
        resolution="Replaced drive end bearing and realigned pump shaft."
    )

    # Compile the graph data
    graph_data = {
        "assets": [pump.model_dump(), valve.model_dump()],
        "documents": [sop_pump.model_dump(mode='json'), manual_valve.model_dump(mode='json')],
        "personnel": [tech_john.model_dump()],
        "maintenance_events": [event_1.model_dump(mode='json')]
    }

    # Save to a mock JSON file
    with open("mock_graph_data.json", "w") as f:
        json.dump(graph_data, f, indent=4)
        
    print("Successfully generated mock_graph_data.json")

if __name__ == "__main__":
    generate_mock_data()
