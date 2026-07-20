import json
import os
import sys

# Add the ontology directory to the path so we can import our schemas
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ontology'))
from schema import AssetNode, DocumentNode, MaintenanceEventNode, PersonnelNode, SemanticChunk

def chunk_and_embed_document(doc_node: DocumentNode) -> list[SemanticChunk]:
    """
    Simulates splitting a document into semantic chunks and generating vector embeddings.
    In a real scenario, this would use LangChain RecursiveCharacterTextSplitter and an embedding model (e.g., text-embedding-3-small).
    """
    print(f"[Vector DB] Chunking document: {doc_node.title}...")
    
    mock_chunks = [
        SemanticChunk(
            chunk_id=f"{doc_node.doc_id}-chunk-1",
            doc_id=doc_node.doc_id,
            content=f"Summary of {doc_node.title}: This document covers operating procedures.",
            embedding=[0.1, -0.05, 0.9, 0.42], # Mock 4-dim embedding instead of 1536
            page_number=1,
            bounding_box=[10.0, 20.0, 200.0, 50.0]
        ),
        SemanticChunk(
            chunk_id=f"{doc_node.doc_id}-chunk-2",
            doc_id=doc_node.doc_id,
            content="Critical warning: Ensure cooling water flow is above 50 GPM before starting.",
            embedding=[-0.8, 0.2, 0.1, 0.99], 
            page_number=2,
            bounding_box=[10.0, 100.0, 200.0, 150.0]
        )
    ]
    return mock_chunks

def upsert_to_neo4j(assets, documents, personnel, events):
    """
    Simulates the Cypher queries to build the Knowledge Graph in Neo4j.
    """
    print("\n--- [Knowledge Graph] Executing Neo4j Upserts ---")
    
    for asset in assets:
        cypher = f"MERGE (a:Asset {{asset_id: '{asset.asset_id}'}}) SET a.name = '{asset.name}', a.type = '{asset.type}'"
        print(f"CYPHER Executed: {cypher}")
        
    for doc in documents:
        cypher = f"MERGE (d:Document {{doc_id: '{doc.doc_id}'}}) SET d.title = '{doc.title}'"
        print(f"CYPHER Executed: {cypher}")
        # Create relation: Asset is documented in Document (mocking finding P-102 in the title)
        if "P-102" in doc.title:
            edge_cypher = f"MATCH (a:Asset {{asset_id: 'P-102'}}), (d:Document {{doc_id: '{doc.doc_id}'}}) MERGE (a)-[:DOCUMENTED_IN]->(d)"
            print(f"CYPHER Executed: {edge_cypher}")

    for event in events:
        cypher = f"MERGE (e:MaintenanceEvent {{event_id: '{event.event_id}'}}) SET e.resolution = '{event.resolution}'"
        print(f"CYPHER Executed: {cypher}")
        # Create relation: Event occurred on Asset
        if "P-102" in event.issue_description:
            edge_cypher = f"MATCH (e:MaintenanceEvent {{event_id: '{event.event_id}'}}), (a:Asset {{asset_id: 'P-102'}}) MERGE (e)-[:OCCURRED_ON]->(a)"
            print(f"CYPHER Executed: {edge_cypher}")

def run_pipeline(data_file: str):
    """
    Main ingestion pipeline to read raw data, structure it, and populate the dual-storage layer.
    """
    print(f"Starting Ingestion Pipeline reading from {data_file}...")
    
    with open(data_file, 'r') as f:
        raw_data = json.load(f)

    # 1. Parse JSON into Pydantic Ontology Models
    assets = [AssetNode(**a) for a in raw_data.get('assets', [])]
    docs = [DocumentNode(**d) for d in raw_data.get('documents', [])]
    personnel = [PersonnelNode(**p) for p in raw_data.get('personnel', [])]
    events = [MaintenanceEventNode(**e) for e in raw_data.get('maintenance_events', [])]
    
    print(f"Parsed {len(assets)} Assets, {len(docs)} Documents, {len(events)} Maintenance Events.")

    # 2. Vector Store Ingestion (Milvus/Pinecone)
    all_chunks = []
    for doc in docs:
        chunks = chunk_and_embed_document(doc)
        all_chunks.extend(chunks)
        
    print(f"Successfully vectorized {len(all_chunks)} semantic chunks for hybrid RAG.")

    # 3. Knowledge Graph Ingestion (Neo4j)
    upsert_to_neo4j(assets, docs, personnel, events)
    
    print("\nIngestion Pipeline Complete! The system is now ready for Agentic Retrieval.")

if __name__ == "__main__":
    # Point to the mock data generated in step 1.2
    mock_file = os.path.join(os.path.dirname(__file__), '..', '..', 'mock_graph_data.json')
    run_pipeline(mock_file)
