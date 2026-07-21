import os
import re
import time
import difflib
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
        from src.ontology.neo4j_client import Neo4jClient
        self.neo4j_client = Neo4jClient()
        self.router = SemanticRouter()
        
        self.rca_agent = RootCauseAnalysisAgent(self.neo4j_client)
        self.compliance_agent = ComplianceAgent(self.neo4j_client)
        self.maintenance_agent = MaintenanceAgent(self.neo4j_client)
        self.general_copilot = GeneralCopilotAgent()
        
        self.critic = CriticAgent(self.neo4j_client)

    def _extract_asset_id(self, query: str) -> str:
        match = re.search(r'[a-zA-Z]-\d+', query)
        return match.group(0).upper() if match else "UNKNOWN_ASSET"

    def _correct_typos(self, query: str) -> str:
        vocab = [
            "vibration", "overheating", "compliance", "maintenance", 
            "preventative", "pump", "valve", "tank", "OSHA", "standards",
            "experiencing", "safety", "schedule", "preventive"
        ]
        words = query.split()
        corrected_words = []
        for word in words:
            clean_word = re.sub(r'[^\w\-]', '', word)
            if len(clean_word) < 4 or re.match(r'[A-Za-z]-\d+', clean_word):
                corrected_words.append(word)
                continue

            matches = difflib.get_close_matches(clean_word.lower(), [v.lower() for v in vocab], n=1, cutoff=0.75)
            if matches:
                matched_word = next(v for v in vocab if v.lower() == matches[0])
                corrected_words.append(word.replace(clean_word, matched_word))
            else:
                corrected_words.append(word)
        return " ".join(corrected_words)

    def process_query(self, query: str) -> dict:
        trace_logs = []
        start_time = time.time()
        
        original_query = query
        query = self._correct_typos(query)
        if query != original_query:
            trace_logs.append({"step": "Typo Correction", "detail": f"Corrected to: '{query}'", "time": "0.01s"})
        
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
