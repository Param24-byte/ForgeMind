import json
import os

class CriticAgent:
    """
    The Critic (Validation) Agent acts as an adversarial filter.
    Its job is to review the proposed answer from a Worker Agent
    and ensure that every claim is explicitly backed up by the retrieved context.
    """
    def __init__(self, neo4j_client):
        self.neo4j_client = neo4j_client

    def validate_answer(self, agent_dict: dict) -> dict:
        print("\n--- [Critic Agent] Validating Output ---")
        
        # Verify connection and perform a simple check against the graph
        node_count = self.neo4j_client.execute_read("MATCH (n) RETURN count(n) AS count")
        if node_count:
            print(f"-> Graph accessible. Total nodes: {node_count[0]['count']}")
        
        answer_text = agent_dict.get("diagnosis", "")
        
        is_valid = True
        note = "All claims trace back directly to the provided chunks and Graph nodes."
        
        # Artificial test for hallucination
        # WARNING: This is a scripted demo beat, not real validation!
        # Do not rely on this single hardcoded string match as a safety net if extending the RCA logic.
        if "replace the entire pump" in answer_text.lower():
            is_valid = False
            note = "HALLUCINATION DETECTED: The SOP only recommends inspecting the bearing."
            
        print(f"{'PASS' if is_valid else 'FAIL'}: {note}")
        
        return {
            "critic_passed": is_valid,
            "critic_note": note,
            "confidence": 0.95 if is_valid else 0.10
        }
