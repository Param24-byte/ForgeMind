class ComplianceAgent:
    def __init__(self, mock_data_path: str):
        pass

    def check_compliance(self, query: str) -> dict:
        diagnosis = "OSHA 1910.212 requires machine guarding for rotating parts. Ensure lockout/tagout procedures are followed before approaching the equipment."
        return {
            "diagnosis": diagnosis,
            "draft_wo": None,
            "citations": [
                {"type": "vector", "text": "OSHA 1910.212(a)(1)"}
            ]
        }
