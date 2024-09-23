from django.urls import path

from . import views

urlpatterns = [
    path("trigger_report/", views.TriggerReportAPIView.as_view(), name="trigger_report"),
    path("get_report/", views.GetReportAPIView.as_view(), name="get_report"),
]