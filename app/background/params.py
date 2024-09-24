class TaskParams:
    """Paramaters for processing the task in background, so that we know what to expect in the params."""

    def __init__(self, report_id: str):
        self.report_id = report_id

    def __repr__(self):
        return f"TaskParams(report_id={self.report_id})"
