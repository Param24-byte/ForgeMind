class GeneralCopilotAgent:
    def __init__(self):
        pass

    def answer(self, query: str) -> dict:
        diagnosis = "I am the general operations copilot. I can help you query maintenance histories, read standard operating procedures, and draft work orders. Please ask me about a specific asset like 'P-102'."
        return {
            "diagnosis": diagnosis,
            "draft_wo": None,
            "citations": []
        }
