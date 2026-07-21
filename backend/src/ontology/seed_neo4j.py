import os
import sys
import json
from src.ontology.neo4j_client import Neo4jClient

def seed_database():
    mock_file = os.path.join(os.path.dirname(__file__), '..', '..', 'mock_graph_data.json')
    if not os.path.exists(mock_file):
        print(f"Mock data file not found at {mock_file}. Cannot seed database.")
        sys.exit(1)
        
    with open(mock_file, 'r') as f:
        data = json.load(f)
        
    client = Neo4jClient()
    if not client.driver:
        print("Failed to initialize Neo4j client. Check credentials.")
        sys.exit(1)
        
    print("Clearing existing data...")
    client.execute_write("MATCH (n) DETACH DELETE n")
    
    print("Seeding Assets...")
    for asset in data.get("assets", []):
        asset.setdefault("manufacturer", "Unknown")
        client.execute_write(
            """
            CREATE (a:Asset {
                asset_id: $asset_id,
                name: $name,
                type: $type,
                location: $location,
                manufacturer: $manufacturer
            })
            """,
            asset
        )
        
    print("Seeding Documents...")
    for doc in data.get("documents", []):
        doc.setdefault("version", "1.0")
        client.execute_write(
            """
            CREATE (d:Document {
                doc_id: $doc_id,
                title: $title,
                doc_type: $doc_type,
                version: $version
            })
            """,
            doc
        )
        # Create relation to Asset based on naming convention in mock
        if "P-102" in doc.get("title", ""):
            client.execute_write("MATCH (a:Asset {asset_id: 'P-102'}), (d:Document {doc_id: $doc_id}) MERGE (a)-[:DOCUMENTED_IN]->(d)", doc)
        if "Control Valve" in doc.get("title", ""):
            client.execute_write("MATCH (a:Asset {asset_id: 'V-991'}), (d:Document {doc_id: $doc_id}) MERGE (a)-[:DOCUMENTED_IN]->(d)", doc)

    print("Seeding Personnel...")
    for person in data.get("personnel", []):
        client.execute_write(
            """
            CREATE (p:Personnel {
                employee_id: $employee_id,
                name: $name,
                role: $role,
                certification_level: $certification_level
            })
            """,
            person
        )
        
    print("Seeding Maintenance Events...")
    for event in data.get("maintenance_events", []):
        client.execute_write(
            """
            CREATE (e:MaintenanceEvent {
                event_id: $event_id,
                work_order_id: $work_order_id,
                date: $date,
                issue_description: $issue_description,
                resolution: $resolution
            })
            """,
            event
        )
        # Create relation to Asset
        if "P-102" in event.get("issue_description", ""):
            client.execute_write("MATCH (a:Asset {asset_id: 'P-102'}), (e:MaintenanceEvent {event_id: $event_id}) MERGE (e)-[:OCCURRED_ON]->(a)", event)

    print("Seeding complete!")
    client.close()

if __name__ == "__main__":
    seed_database()
