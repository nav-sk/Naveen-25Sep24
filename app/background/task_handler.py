from django.dispatch import receiver
from .task_signal import task_signal
from .tasks import generate_report
from .params import TaskParams


@receiver(task_signal, weak=False)
def task_handler(*args, **kwargs):
    """Handle the task signal and start the report generation task in background powered by Celery."""
    task_params = TaskParams(report_id=kwargs.get("report_id"))
    generate_report.delay(report_id=task_params.report_id)
