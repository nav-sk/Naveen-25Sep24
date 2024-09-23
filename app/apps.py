from django.apps import AppConfig


class AppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app"

    def ready(self) -> None:
        from .background.task_signal import task_signal
        from .background.task_handler import task_handler

        task_signal.connect(task_handler)
