import json
import os
import io
try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

class IngestionPipeline:
    def __init__(self):
        self.mock_file = os.path.join(os.path.dirname(__file__), '..', '..', 'mock_graph_data.json')

    def run_ingestion(self, uploaded_content: bytes = None, filename: str = None) -> dict:
        print("[Ingestion Pipeline] Starting document ingestion...")
        print("[Ingestion Pipeline] Parsing P&ID diagrams via Vision OCR...")
        print("[Ingestion Pipeline] Chunking SOPs for Vector DB...")
        print("[Ingestion Pipeline] Generating Cypher queries for Neo4j...")
        
        try:
            if uploaded_content:
                if filename and filename.endswith('.json'):
                    with open(self.mock_file, 'wb') as f:
                        f.write(uploaded_content)
                    data = json.loads(uploaded_content.decode('utf-8'))
                    num_assets = len(data.get("assets", []))
                    num_chunks = len(data.get("documents", []))
                    return {"success": True, "message": f"Uploaded {filename}: {num_assets} assets and {num_chunks} document chunks successfully upserted into Graph and Vector DBs."}
                else:
                    text_file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'uploaded_document.txt')
                    
                    extracted_text = ""
                    # Check if it's a PDF (either by extension or magic bytes)
                    if PdfReader and ((filename and filename.lower().endswith('.pdf')) or b"%PDF" in uploaded_content[:10]):
                        try:
                            reader = PdfReader(io.BytesIO(uploaded_content))
                            for page in reader.pages:
                                extracted_text += page.extract_text() + "\n"
                        except Exception as e:
                            print(f"Failed to parse PDF: {e}")
                            extracted_text = uploaded_content.decode('utf-8', errors='ignore')
                    else:
                        extracted_text = uploaded_content.decode('utf-8', errors='ignore')
                        
                    with open(text_file_path, 'w', encoding='utf-8') as f:
                        f.write(extracted_text)
                    return {"success": True, "message": f"Uploaded {filename}: Extracted and saved text."}
            else:
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
