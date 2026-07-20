import json
import os
import sys

# Need ActionEngine to draft WO
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'governance'))
from action_engine import ActionEngine

class RootCauseAnalysisAgent:
    """
    The RCA Agent is responsible for diagnosing equipment failures.
    It simulates querying the Neo4j Knowledge Graph to find maintenance history,
    and querying the Vector DB to find relevant SOPs and manuals.
    """
    def __init__(self, mock_data_path: str):
        self.mock_data_path = mock_data_path
        self.action_engine = ActionEngine()
        
    def _mock_graph_retrieval(self, asset_id: str) -> dict:
        """Simulates a Cypher query to retrieve maintenance history for an asset."""
        print(f"[RCA Agent] Traversing Graph: MATCH (e:MaintenanceEvent)-[:OCCURRED_ON]->(a:Asset {{asset_id: '{asset_id}'}}) RETURN e")
        with open(self.mock_data_path, 'r') as f:
            data = json.load(f)
            
        # Match events by asset_id explicitly if present, or substring on issue description
        history = [e for e in data.get('maintenance_events', []) if asset_id in e.get('issue_description', '') or asset_id == e.get('asset_id')]
        return history[0] if history else None

    def _mock_vector_retrieval(self, query: str) -> list[str]:
        """Simulates a semantic search in Milvus/Pinecone."""
        print(f"[RCA Agent] Vector Search: Retrieving chunks matching '{query}'")
        return [
            "Critical warning: Ensure cooling water flow is above 50 GPM before starting.",
            "If bearing vibration is high, inspect for shaft misalignment and replace drive end bearing."
        ]

    def diagnose_failure(self, asset_id: str, symptom: str) -> dict:
        print(f"\n--- [RCA Agent] Initiating Diagnosis for {asset_id} ---")
        print(f"Symptom Reported: {symptom}")
        
        # 1. Retrieve Historical Context from Graph
        history = self._mock_graph_retrieval(asset_id)
        if history:
            print(f"-> Graph Context Found: {asset_id} previously had issue '{history['issue_description']}' on {history['date']}")
        else:
            print(f"-> Graph Context: No previous maintenance history found for {asset_id}.")
            
        # 2. Retrieve Procedural Context from Vector DB
        sop_chunks = self._mock_vector_retrieval(symptom)
        print(f"-> Vector Context Found: Found {len(sop_chunks)} relevant SOP chunks.")
        
        # 3. Synthesize the Answer (Simulating the LLM generation)
        print("\n[RCA Agent] Synthesizing final diagnosis via LLM...")
        
        diagnosis = (
            f"DIAGNOSIS REPORT FOR {asset_id}:\n"
            f"Based on the reported symptom '{symptom}', the Vector DB SOP states that high vibration "
            f"often indicates shaft misalignment. \n\n"
        )
        
        if history:
            diagnosis += (
                f"Furthermore, traversing the Knowledge Graph reveals that {asset_id} had a similar issue on "
                f"May 10, 2026 (Work Order {history.get('work_order_id', 'Unknown')}), where the drive end bearing was replaced. \n\n"
            )
        else:
            diagnosis += "There is no recorded historical maintenance for this specific issue on this asset.\n\n"
            
        diagnosis += (
            f"RECOMMENDATION: It is highly probable the shaft has come out of alignment again, causing premature bearing wear. "
            f"Please halt operation and inspect the drive end bearing."
        )
        
        # Draft a Work Order automatically
        draft_wo = self.action_engine.draft_work_order(asset_id, diagnosis)
        
        return {
            "diagnosis": diagnosis,
            "draft_wo": draft_wo,
            "citations": [
                {"type": "graph", "text": f"Event EVT-2026-001 for {asset_id}" if history else "No Graph History"},
                {"type": "vector", "text": "SOP: P-102 Manual (Page 2)"}
            ]
        }
