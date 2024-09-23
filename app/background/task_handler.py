from django.dispatch import receiver
from .task_signal import task_signal
from .tasks import generate_report

@receiver(task_signal, weak = False)
def task_handler(*args, **kwargs):
    report_id = kwargs.get("report_id")
    generate_report.delay(report_id = report_id)

