from rest_framework import serializers

from .models import Report


class TriggerReportResponseSerializer(serializers.Serializer):
    """Serializer for TriggerReportAPIView"""
    report_id = serializers.CharField()


class GetReportRunningResponseSerializer(serializers.Serializer):
    """Serializer for GetReportAPIView when report is running"""
    status = serializers.CharField()

    class Meta:
        model = Report


class GetReportCompleteResponseSerializer(serializers.Serializer):
    """Serializer for GetReportAPIView when report is complete"""
    status = serializers.CharField()
    report = serializers.CharField()

    class Meta:
        model = Report
