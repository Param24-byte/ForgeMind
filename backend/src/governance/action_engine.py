import time
from datetime import datetime

class ActionEngine:
    """
    The Action Engine bridges passive AI diagnostics with active enterprise execution.
    It drafts payloads for external systems (e.g., SAP, Maximo) and manages the 
    Human-in-the-Loop (HITL) approval workflow.
    """
    
    def draft_work_order(self, asset_id: str, diagnosis_report: str) -> dict:
        print(f"\n[Action Engine] Parsing diagnosis to draft SAP Work Order for {asset_id}...")
        
        # Simulating extraction of key action items from the diagnosis report
        payload = {
            "api_endpoint": "https://api.sap.com/s4hana/maintenance/WorkOrders",
            "method": "POST",
            "body": {
                "AssetID": asset_id,
                "Priority": "CRITICAL",
                "OrderType": "PM01",
                "Description": "Inspect and Realign Drive End Bearing",
                "LongText": diagnosis_report[:100] + "...",
                "TargetDate": datetime.now().strftime("%Y-%m-%d"),
                "RequiredParts": ["Bearing-6205-ZZ"]
            }
        }
        
        print(f"[Action Engine] Draft Payload Created:")
        print(payload)
        return payload

    def await_hitl_approval(self, payload: dict, simulate_user_action: str = "approve") -> bool:
        """
        Simulates the workflow pausing and waiting for a supervisor to click 'Approve' or 'Reject' 
        on the React frontend Dashboard.
        """
        print("\n--- [HITL Workflow] Execution Paused ---")
        print("Waiting for Supervisor Role Authorization via API Gateway...")
        time.sleep(1) # Simulating network/human wait
        
        if simulate_user_action.lower() == "approve":
            print(f"PASS: Supervisor Approved. Executing API Call to SAP...")
            return True
        else:
            print(f"FAIL: Supervisor Rejected the Action. Routing to Knowledge Evolution.")
            return False

class KnowledgeEvolutionEngine:
    """
    If a human expert rejects an AI recommendation, this engine degrades the confidence weight
    of the specific edge in the Knowledge Graph that led to that answer, preventing future hallucinations.
    """
    def process_rejection(self, asset_id: str, feedback_reason: str):
        print(f"\n[Knowledge Evolution] Processing Rejection Event for {asset_id}")
        print(f"Expert Feedback: '{feedback_reason}'")
        
        # Simulating Cypher query to degrade the weight of the SOP linkage
        cypher = (
            f"MATCH (a:Asset {{asset_id: '{asset_id}'}})-[r:DOCUMENTED_IN]->(d:Document) "
            f"SET r.confidence_weight = r.confidence_weight - 0.2 "
            f"RETURN r.confidence_weight"
        )
        print(f"CYPHER Executed: {cypher}")
        print("Graph linkage weight degraded. The RCA Agent is less likely to recommend this path in the future.")


if __name__ == "__main__":
    action_engine = ActionEngine()
    evolution_engine = KnowledgeEvolutionEngine()
    
    # Mocking the flow from Phase 2
    asset = "P-102"
    diagnosis = "Shaft misalignment detected. Replace drive end bearing."
    
    # 3.1 Draft Action
    draft_payload = action_engine.draft_work_order(asset, diagnosis)
    
    # 3.2 Simulate HITL - First we simulate an approval
    action_engine.await_hitl_approval(draft_payload, simulate_user_action="approve")
    
    # 3.3 Simulate HITL - Now we simulate a rejection (e.g. human expert says "No, it's actually the seal")
    print("\n--------------------------------------------------")
    print("Simulating a REJECTION scenario to trigger Evolution")
    print("--------------------------------------------------")
    approved = action_engine.await_hitl_approval(draft_payload, simulate_user_action="reject")
    if not approved:
        evolution_engine.process_rejection(asset, "SOP is outdated. Issue is actually the mechanical seal, not the bearing.")
