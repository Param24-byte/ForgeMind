class ComplianceAgent:
    def __init__(self, neo4j_client):
        self.neo4j_client = neo4j_client

    def check_compliance(self, query: str) -> dict:
        docs = self.neo4j_client.execute_read("MATCH (d:Document) RETURN d.title AS title LIMIT 3")
        doc_titles = [d['title'] for d in docs] if docs else []
        
        diagnosis = "OSHA 1910.212 requires machine guarding for rotating parts. Ensure lockout/tagout procedures are followed before approaching the equipment."
        if doc_titles:
            diagnosis += f"\nRelevant Documents found in Graph: {', '.join(doc_titles)}"

        return {
            "diagnosis": diagnosis,
            "draft_wo": None,
            "citations": [
                {"type": "graph", "text": f"Graph Docs: {len(doc_titles)}"},
                {"type": "vector", "text": "OSHA 1910.212(a)(1)"}
            ]
        }
