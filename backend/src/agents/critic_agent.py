import json
import os

class CriticAgent:
    """
    The Critic (Validation) Agent acts as an adversarial filter.
    Its job is to review the proposed answer from a Worker Agent (like RCA)
    and ensure that every claim is explicitly backed up by the retrieved context.
    If it detects a hallucination, it rejects the answer.
    """
    def __init__(self, mock_data_path: str):
        self.mock_data_path = mock_data_path

    def validate_answer(self, agent_answer: str, retrieved_context: list[str]) -> dict:
        print("\n--- [Critic Agent] Validating Output ---")
        print("Checking claims against original document boundaries...")
        
        # Simulating hallucination detection logic
        # A real implementation would prompt an LLM to check if `agent_answer` is strictly entailed by `retrieved_context`.
        
        is_valid = True
        reasoning = "All claims (shaft misalignment, past work order WO-88123) trace back directly to the provided Vector SOP chunks and Graph Maintenance nodes."
        
        # Artificial test for hallucination
        if "replace the entire pump" in agent_answer.lower():
            is_valid = False
            reasoning = "HALLUCINATION DETECTED: The SOP only recommends inspecting the bearing. It does not recommend replacing the entire pump."
            
        if is_valid:
            print("PASS: Validation PASSED: No hallucinations detected. Confidence High.")
            return {"status": "PASSED", "confidence": 0.95, "reasoning": reasoning}
        else:
            print("FAIL: Validation FAILED: Hallucination detected.")
            return {"status": "FAILED", "confidence": 0.10, "reasoning": reasoning}

if __name__ == "__main__":
    # Mock test of the Critic Agent
    critic = CriticAgent("mock_data.json")
    
    # Example 1: Valid Answer
    valid_answer = "Based on SOP, high vibration means shaft misalignment. History shows WO-88123 replaced the bearing."
    context = ["high vibration means shaft misalignment", "WO-88123 replaced bearing"]
    critic.validate_answer(valid_answer, context)
    
    # Example 2: Hallucinated Answer
    invalid_answer = "Based on SOP, high vibration means we must replace the entire pump immediately."
    critic.validate_answer(invalid_answer, context)
