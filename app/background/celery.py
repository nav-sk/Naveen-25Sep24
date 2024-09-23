import os
from celery import Celery, Task


class CeleryTask(Task):
    def before_start(self, task_id, args, kwargs):
        return super().before_start(task_id, args, kwargs)

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        return super().after_return(status, retval, task_id, args, kwargs, einfo)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        return super().on_failure(exc, task_id, args, kwargs, einfo)


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
app = Celery("background_task", task_cls="app.background.celery:CeleryTask")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
