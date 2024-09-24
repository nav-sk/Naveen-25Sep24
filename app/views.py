from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    GetReportCompleteResponseSerializer,
    GetReportRunningResponseSerializer,
    TriggerReportResponseSerializer,
)
from .services import ReportService


class TriggerReportAPIView(APIView):
    def get(self, request):
        report_id = ReportService.start_report_generation()
        serializer = TriggerReportResponseSerializer({"report_id": report_id})
        return Response(serializer.data)


class GetReportAPIView(APIView):
    def get(self, request):
        params = request.query_params
        report = ReportService.test_report_generation(report_id=params.get("report_id"))
        # If the report is running, return only the status
        if report.status == "Running":
            serializer = GetReportRunningResponseSerializer(report)
        else:
            # If the report is complete, return the status and the report data
            serializer = GetReportCompleteResponseSerializer(report)
        return Response(serializer.data)
