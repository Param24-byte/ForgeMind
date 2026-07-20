from enum import Enum
from pydantic import BaseModel

class AgentRoute(Enum):
    RCA_AGENT = "Root Cause Analysis (RCA) Agent"
    COMPLIANCE_AGENT = "Compliance & Safety Agent"
    MAINTENANCE_AGENT = "Maintenance Planning Agent"
    GENERAL_COPILOT = "General Knowledge Copilot"

class RouteDecision(BaseModel):
    selected_agent: AgentRoute
    confidence: float
    reason: str

class SemanticRouter:
    """
    The Semantic Router is the Supervisor agent's first step.
    It takes an incoming natural language query from a technician and determines
    which specialized agent swarm should handle the request.
    
    In production, this would use a fast, cheap LLM or an Embedding Cache (Redis).
    """
    
    def __init__(self):
        # Mock keyword heuristics to simulate semantic similarity routing
        self.rca_keywords = ["why", "broke", "overheating", "failed", "vibration", "cause", "leak"]
        self.compliance_keywords = ["osha", "iso", "regulation", "safe", "permit", "allowed", "audit"]
        self.maintenance_keywords = ["schedule", "when was", "history", "order", "replace", "parts"]
        
    def route_query(self, query: str) -> RouteDecision:
        query_lower = query.lower()
        
        print(f"\n[Semantic Router] Analyzing Intent for query: '{query}'")
        
        if any(keyword in query_lower for keyword in self.rca_keywords):
            return RouteDecision(
                selected_agent=AgentRoute.RCA_AGENT,
                confidence=0.92,
                reason="Query contains diagnostics/failure terminology."
            )
            
        elif any(keyword in query_lower for keyword in self.compliance_keywords):
            return RouteDecision(
                selected_agent=AgentRoute.COMPLIANCE_AGENT,
                confidence=0.88,
                reason="Query explicitly asks about safety or regulatory compliance."
            )
            
        elif any(keyword in query_lower for keyword in self.maintenance_keywords):
            return RouteDecision(
                selected_agent=AgentRoute.MAINTENANCE_AGENT,
                confidence=0.85,
                reason="Query focuses on historical actions or future planning."
            )
            
        # Fallback
        return RouteDecision(
            selected_agent=AgentRoute.GENERAL_COPILOT,
            confidence=0.60,
            reason="No specific technical domain detected, falling back to general QA."
        )

if __name__ == "__main__":
    router = SemanticRouter()
    
    queries = [
        "Why is Pump P-102 overheating and vibrating so much?",
        "Do I need a hot work permit to weld near the cooling tower?",
        "When was the last time we replaced the bearings on V-991?",
        "What does the platform do?"
    ]
    
    for q in queries:
        decision = router.route_query(q)
        print(f"--> Routed to: {decision.selected_agent.value} (Confidence: {decision.confidence})")
        print(f"--> Reason: {decision.reason}")
