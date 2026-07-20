class MaintenanceAgent:
    def __init__(self, mock_data_path: str):
        pass

    def check_maintenance(self, query: str) -> dict:
        diagnosis = "Based on the CMMS schedule, this asset is due for a preventative maintenance overhaul next week. The last work order was completed 6 months ago."
        return {
            "diagnosis": diagnosis,
            "draft_wo": None,
            "citations": [
                {"type": "graph", "text": "SAP PM Schedule"}
            ]
        }
