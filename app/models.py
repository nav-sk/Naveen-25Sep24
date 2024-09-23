from django.db import models
import uuid


class Store(models.Model):
    id = models.CharField(
        max_length=36, primary_key=True, default=uuid.uuid4, editable=False
    )
    store_id = models.CharField(max_length=32, unique=True)
    timezone = models.CharField(max_length=64, default="America/Chicago")

    def __repr__(self) -> str:
        return f"{self.store_id} - {self.timezone}"


class StoreHours(models.Model):
    id = models.CharField(
        max_length=36, primary_key=True, default=uuid.uuid4, editable=False
    )
    day_of_week = models.IntegerField(default=0)
    start_time_local = models.TimeField(default="00:00:00")
    end_time_local = models.TimeField(default="23:59:59")
    store = models.ForeignKey(Store, on_delete=models.CASCADE)

    def __repr__(self) -> str:
        return f"{self.store.store_id} - {self.day_of_week} - {self.start_time} - {self.end_time}"


class StoreStatus(models.Model):
    id = models.CharField(
        max_length=36, primary_key=True, default=uuid.uuid4, editable=False
    )
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=32, choices=[("active", "active"), ("inactive", "inactive")]
    )
    timestamp_utc = models.DateTimeField(null=False)

    def __repr__(self) -> str:
        return f"{self.store.store_id} - {self.status} - {self.timestamp_utc}"


class Report(models.Model):
    id = models.CharField(
        max_length=36, primary_key=True, default=uuid.uuid4, editable=False
    )
    report_id = models.CharField(max_length=36, unique=True)
    report = models.TextField()
    generated_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=32,
        default="Running",
        choices=[("Running", "Running"), ("Complete", "Complete")],
    )
