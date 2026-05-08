from django.urls import path

from .views import ExportDownloadView, ExportRequestView, ExportStatusView

urlpatterns = [
    # CSV veya Excel export isteği başlat
    path(
        "exports/sensor-data/<str:fmt>/",
        ExportRequestView.as_view(),
        name="export-request",
    ),
    # Async job durumu
    path(
        "exports/<uuid:job_id>/status/",
        ExportStatusView.as_view(),
        name="export-status",
    ),
    # Tamamlanmış dosyayı indir
    path(
        "exports/<uuid:job_id>/download/",
        ExportDownloadView.as_view(),
        name="export-download",
    ),
]
