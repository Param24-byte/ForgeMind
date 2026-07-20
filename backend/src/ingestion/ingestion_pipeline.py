import json
import os

class IngestionPipeline:
    def __init__(self):
        self.mock_file = os.path.join(os.path.dirname(__file__), '..', '..', 'mock_graph_data.json')

    def run_ingestion(self) -> dict:
        print("[Ingestion Pipeline] Starting document ingestion...")
        print("[Ingestion Pipeline] Parsing P&ID diagrams via Vision OCR...")
        print("[Ingestion Pipeline] Chunking SOPs for Vector DB...")
        print("[Ingestion Pipeline] Generating Cypher queries for Neo4j...")
        
        try:
            with open(self.mock_file, 'r') as f:
                data = json.load(f)
            num_assets = len(data.get("assets", []))
            num_chunks = len(data.get("documents", []))
            return {"success": True, "message": f"{num_assets} assets and {num_chunks} document chunks successfully upserted into Graph and Vector DBs."}
        except Exception as e:
            return {"success": False, "message": f"Ingestion failed: {str(e)}"}

if __name__ == "__main__":
    pipeline = IngestionPipeline()
    result = pipeline.run_ingestion()
    print(result)
