import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

class Neo4jClient:
    def __init__(self):
        load_dotenv()
        self.uri = os.getenv("NEO4J_URI", "")
        self.user = os.getenv("NEO4J_USERNAME", "")
        self.password = os.getenv("NEO4J_PASSWORD", "")
        
        if not self.uri or not self.user or not self.password:
            print("[Neo4jClient] WARNING: Neo4j credentials not found in environment. Please check your .env file.")
            self.driver = None
        else:
            try:
                self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
                print(f"[Neo4jClient] Connected successfully to {self.uri}")
            except Exception as e:
                print(f"[Neo4jClient] ERROR: Failed to connect to Neo4j. {e}")
                self.driver = None

    def close(self):
        if self.driver:
            self.driver.close()
            
    def execute_read(self, cypher: str, parameters=None):
        if not self.driver:
            print("[Neo4jClient] ERROR: Driver not initialized. Returning None.")
            return None
        with self.driver.session() as session:
            try:
                result = session.run(cypher, parameters or {})
                return [record.data() for record in result]
            except Exception as e:
                print(f"[Neo4jClient] Read Error: {e}")
                return None
                
    def execute_write(self, cypher: str, parameters=None):
        if not self.driver:
            print("[Neo4jClient] ERROR: Driver not initialized. Returning None.")
            return None
        with self.driver.session() as session:
            try:
                result = session.run(cypher, parameters or {})
                return [record.data() for record in result]
            except Exception as e:
                print(f"[Neo4jClient] Write Error: {e}")
                return None
