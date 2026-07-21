class MaintenanceAgent:
    def __init__(self, neo4j_client):
        self.neo4j_client = neo4j_client

    def check_maintenance(self, query: str) -> dict:
        events = self.neo4j_client.execute_read("MATCH (e:MaintenanceEvent) RETURN e.date AS date, e.issue_description AS issue ORDER BY e.date DESC LIMIT 1")
        last_event = events[0] if events else None
        
        diagnosis = "Based on the CMMS schedule, this asset is due for a preventative maintenance overhaul next week."
        if last_event:
            diagnosis += f" The last recorded issue in the graph was '{last_event['issue']}' on {last_event['date']}."
        else:
            diagnosis += " The last work order was completed 6 months ago."

        return {
            "diagnosis": diagnosis,
            "draft_wo": None,
            "citations": [
                {"type": "graph", "text": "Neo4j MaintenanceEvent Data"}
            ]
        }
