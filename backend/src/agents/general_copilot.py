import os

class GeneralCopilotAgent:
    def __init__(self):
        pass

    def answer(self, query: str) -> dict:
        diagnosis = "I am the general operations copilot. I can help you query maintenance histories, read standard operating procedures, and draft work orders. Please ask me about a specific asset like 'P-102'."
        
        text_file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'uploaded_document.txt')
        if os.path.exists(text_file_path):
            try:
                with open(text_file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                query_words = set(w.lower() for w in query.split() if len(w) > 3)
                results = []
                for line in lines:
                    if any(w in line.lower() for w in query_words):
                        results.append(line.strip())
                if results:
                    diagnosis = f"Based on the uploaded document, I found the following relevant information:\n\n"
                    for r in results[:3]:
                        diagnosis += f"- {r}\n"
            except Exception:
                pass

        return {
            "diagnosis": diagnosis,
            "draft_wo": None,
            "citations": []
        }
