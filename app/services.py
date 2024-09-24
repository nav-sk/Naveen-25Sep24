from .background.task_signal import task_signal
from .models import Report


class ReportService:
    """Service class for report generation"""

    @classmethod
    def start_report_generation(cls) -> str:
        """Start the report generation process in the background and return the report ID."""
        report = Report.objects.create()
        task_signal.send(sender=cls.__name__, report_id=report.report_id)
        return report.report_id

    @classmethod
    def test_report_generation(cls, report_id: str) -> Report:
        """Get the report data for the given report ID."""
        report = Report.objects.get(report_id=report_id)
        return report
