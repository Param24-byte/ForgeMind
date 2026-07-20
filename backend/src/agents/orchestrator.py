import os
from semantic_router import SemanticRouter, AgentRoute
from rca_agent import RootCauseAnalysisAgent
from critic_agent import CriticAgent

class AgentOrchestrator:
    """
    The main Orchestrator that receives a user query, routes it to the correct agent,
    gets a drafted response, and passes it through the Critic for validation.
    """
    def __init__(self):
        self.mock_file = os.path.join(os.path.dirname(__file__), '..', '..', 'mock_graph_data.json')
        self.router = SemanticRouter()
        self.rca_agent = RootCauseAnalysisAgent(self.mock_file)
        self.critic = CriticAgent(self.mock_file)

    def process_query(self, asset_id: str, query: str) -> dict:
        print(f"\n==================================================")
        print(f"ORCHESTRATOR RECIEVED QUERY: '{query}' for {asset_id}")
        print(f"==================================================")
        
        # Step 1: Routing
        route_decision = self.router.route_query(query)
        
        # Step 2: Agent Execution
        if route_decision.selected_agent == AgentRoute.RCA_AGENT:
            draft_answer = self.rca_agent.diagnose_failure(asset_id, query)
            # Mock context that the agent would have retrieved
            context = ["high vibration indicates shaft misalignment", "WO-88123 replaced drive end bearing"]
        else:
            draft_answer = "This agent is not yet implemented for the mock demo."
            context = []
            
        # Step 3: Critic Validation
        validation = self.critic.validate_answer(draft_answer, context)
        
        if validation["status"] == "PASSED":
            return {
                "success": True,
                "final_answer": draft_answer,
                "confidence": validation["confidence"]
            }
        else:
            return {
                "success": False,
                "error": "The generated answer failed validation due to detected hallucinations.",
                "reasoning": validation["reasoning"]
            }

if __name__ == "__main__":
    orchestrator = AgentOrchestrator()
    result = orchestrator.process_query(asset_id="P-102", query="Why is it experiencing high vibration and overheating?")
    
    print("\n--- FINAL OUTPUT TO USER ---")
    if result["success"]:
        print(result["final_answer"])
    else:
        print(f"ERROR: {result['error']}\nDetails: {result['reasoning']}")
