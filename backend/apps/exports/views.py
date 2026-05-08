"""
Export endpoint'leri — D-05 hibrit sync/async mantığı.

10k satırdan az → dosyayı doğrudan döndür (sync).
10k satır veya fazlası → job_id döndür, Celery arka planda işler.
"""

import logging
import os

from django.conf import settings
from django.http import FileResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ExportJob
from .serializers import ExportJobSerializer, ExportRequestSerializer
from .tasks import _query_sensor_data, generate_export_async

logger = logging.getLogger(__name__)

THRESHOLD = getattr(settings, "EXPORT_SYNC_ROW_THRESHOLD", 10000)


class ExportRequestView(APIView):
    """POST /exports/sensor-data/{format}/ — export isteği başlat."""

    permission_classes = [IsAuthenticated]

    def post(self, request, fmt):
        if fmt not in (ExportJob.CSV, ExportJob.EXCEL):
            return Response(
                {"detail": "Geçersiz format. Seçenekler: csv, excel", "code": "invalid_format"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ExportRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        filters = {k: str(v) for k, v in serializer.validated_data.items()}

        # Satır sayısını tahmin et — sync mi async mi karar ver
        try:
            df = _query_sensor_data(filters, request.user.id)
            row_count = len(df)
        except Exception as exc:
            logger.error("Export sorgusu başarısız: %s", exc)
            return Response(
                {"detail": "Veri sorgulanırken hata oluştu.", "code": "query_error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if row_count < THRESHOLD:
            # Sync: dosyayı doğrudan döndür
            return _serve_sync(df, fmt, row_count)

        # Async: job oluştur, kuyruğa al
        job = ExportJob.objects.create(
            requested_by=request.user,
            format=fmt,
            filters=filters,
            row_count=row_count,
        )
        generate_export_async.delay(str(job.job_id))

        return Response(
            {
                "job_id": str(job.job_id),
                "row_count": row_count,
                "status": job.status,
                "detail": "Export kuyruğa alındı. Durum için /exports/{job_id}/status/ adresini kullanın.",
            },
            status=status.HTTP_202_ACCEPTED,
        )


class ExportStatusView(APIView):
    """GET /exports/{job_id}/status/ — job durumunu sorgula."""

    permission_classes = [IsAuthenticated]

    def get(self, request, job_id):
        try:
            job = ExportJob.objects.get(job_id=job_id, requested_by=request.user)
        except ExportJob.DoesNotExist:
            return Response(
                {"detail": "Export işi bulunamadı.", "code": "not_found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(ExportJobSerializer(job).data)


class ExportDownloadView(APIView):
    """GET /exports/{job_id}/download/ — tamamlanmış dosyayı indir."""

    permission_classes = [IsAuthenticated]

    def get(self, request, job_id):
        try:
            job = ExportJob.objects.get(job_id=job_id, requested_by=request.user)
        except ExportJob.DoesNotExist:
            return Response(
                {"detail": "Export işi bulunamadı.", "code": "not_found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if job.status != ExportJob.COMPLETE:
            return Response(
                {
                    "detail": f"Dosya henüz hazır değil. Durum: {job.status}",
                    "code": "not_ready",
                },
                status=status.HTTP_409_CONFLICT,
            )

        if not job.file_path or not os.path.exists(job.file_path):
            return Response(
                {"detail": "Dosya bulunamadı veya süresi dolmuş.", "code": "file_missing"},
                status=status.HTTP_410_GONE,
            )

        content_type = (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            if job.format == ExportJob.EXCEL
            else "text/csv"
        )
        ext = "xlsx" if job.format == ExportJob.EXCEL else "csv"
        filename = f"sensor-data-export.{ext}"

        return FileResponse(
            open(job.file_path, "rb"),
            content_type=content_type,
            as_attachment=True,
            filename=filename,
        )


def _serve_sync(df, fmt: str, row_count: int):
    """Sync export: DataFrame'i HTTP yanıtı olarak döndür."""
    import io

    if fmt == ExportJob.EXCEL:
        buf = io.BytesIO()
        df.to_excel(buf, index=False)
        buf.seek(0)
        response = FileResponse(
            buf,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            filename="sensor-data-export.xlsx",
        )
    else:
        buf = io.StringIO()
        df.to_csv(buf, index=False)
        buf.seek(0)
        response = FileResponse(
            io.BytesIO(buf.getvalue().encode()),
            content_type="text/csv",
            as_attachment=True,
            filename="sensor-data-export.csv",
        )

    response["X-Row-Count"] = str(row_count)
    return response
