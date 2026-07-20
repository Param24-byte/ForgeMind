import os
import re
import time
from src.agents.semantic_router import SemanticRouter, AgentRoute
from src.agents.rca_agent import RootCauseAnalysisAgent
from src.agents.critic_agent import CriticAgent
from src.agents.compliance_agent import ComplianceAgent
from src.agents.maintenance_agent import MaintenanceAgent
from src.agents.general_copilot import GeneralCopilotAgent

class AgentOrchestrator:
    """
    The main Orchestrator that receives a user query, routes it to the correct agent,
    gets a drafted response, and passes it through the Critic for validation.
    """
    def __init__(self):
        self.mock_file = os.path.join(os.path.dirname(__file__), '..', '..', 'mock_graph_data.json')
        self.router = SemanticRouter()
        
        self.rca_agent = RootCauseAnalysisAgent(self.mock_file)
        self.compliance_agent = ComplianceAgent(self.mock_file)
        self.maintenance_agent = MaintenanceAgent(self.mock_file)
        self.general_copilot = GeneralCopilotAgent()
        
        self.critic = CriticAgent(self.mock_file)

    def _extract_asset_id(self, query: str) -> str:
        match = re.search(r'[A-Z]-\d+', query)
        return match.group(0) if match else "UNKNOWN_ASSET"

    def process_query(self, query: str) -> dict:
        trace_logs = []
        start_time = time.time()
        
        asset_id = self._extract_asset_id(query)
        trace_logs.append({"step": "Query Processing", "detail": f"Extracted Asset ID: {asset_id}", "time": "0.01s"})
        
        # Step 1: Routing
        t0 = time.time()
        route_decision = self.router.route_query(query)
        agent_name = route_decision.selected_agent.value
        t1 = time.time()
        trace_logs.append({"step": "Semantic Router", "detail": f"Routed query to {agent_name} (Confidence: {route_decision.confidence:.2f})", "time": f"{t1-t0:.2f}s"})
        
        # Step 2: Agent Execution
        t0 = time.time()
        if route_decision.selected_agent == AgentRoute.RCA_AGENT:
            agent_output = self.rca_agent.diagnose_failure(asset_id, query)
        elif route_decision.selected_agent == AgentRoute.COMPLIANCE_AGENT:
            agent_output = self.compliance_agent.check_compliance(query)
        elif route_decision.selected_agent == AgentRoute.MAINTENANCE_AGENT:
            agent_output = self.maintenance_agent.check_maintenance(query)
        else:
            agent_output = self.general_copilot.answer(query)
            agent_name = "General Copilot"
        t1 = time.time()
        trace_logs.append({"step": f"{agent_name} Execution", "detail": "Retrieved context and synthesized diagnosis.", "time": f"{t1-t0:.2f}s"})
            
        # Step 3: Critic Validation
        t0 = time.time()
        validation = self.critic.validate_answer(agent_output)
        t1 = time.time()
        trace_logs.append({"step": "Critic Validation", "detail": validation["critic_note"], "time": f"{t1-t0:.2f}s"})
        
        total_time = time.time() - start_time
        trace_logs.append({"step": "Total Execution", "detail": "Response ready for delivery.", "time": f"{total_time:.2f}s"})
        
        return {
            "agent_name": agent_name,
            "diagnosis": agent_output.get("diagnosis", ""),
            "citations": agent_output.get("citations", []),
            "draft_work_order": agent_output.get("draft_wo", None),
            "critic_passed": validation["critic_passed"],
            "critic_note": validation["critic_note"],
            "confidence": validation["confidence"],
            "trace": trace_logs
        }
