"""
Export Celery görevleri.
generate_export_async — büyük veri setlerini arka planda CSV/Excel olarak yazar.
cleanup_expired_export_jobs — 7 günden eski tamamlanmış dosyaları siler (Beat: daily 03:00).
"""

import logging
import os
from pathlib import Path

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=2, default_retry_delay=30)
def generate_export_async(self, job_id: str) -> None:
    """
    ExportJob'u işler: sensor_readings'i filtreler, pandas ile yazar,
    dosya yolunu ve satır sayısını günceller.
    """
    from django.conf import settings
    from django.utils.timezone import now, timedelta

    from apps.exports.models import ExportJob

    try:
        job = ExportJob.objects.get(job_id=job_id)
    except ExportJob.DoesNotExist:
        logger.error("ExportJob bulunamadı: %s", job_id)
        return

    job.status = ExportJob.PROCESSING
    job.save(update_fields=["status"])

    try:
        df = _query_sensor_data(job.filters, job.requested_by_id)

        export_root = Path(settings.EXPORT_ROOT)
        export_root.mkdir(parents=True, exist_ok=True)

        ext = "xlsx" if job.format == ExportJob.EXCEL else "csv"
        filename = f"{job.job_id}.{ext}"
        file_path = export_root / filename

        if job.format == ExportJob.EXCEL:
            df.to_excel(file_path, index=False)
        else:
            df.to_csv(file_path, index=False)

        job.status = ExportJob.COMPLETE
        job.file_path = str(file_path)
        job.row_count = len(df)
        job.expires_at = now() + timedelta(days=7)
        job.save(update_fields=["status", "file_path", "row_count", "expires_at"])

        logger.info("Export tamamlandı: job=%s format=%s rows=%s", job_id, job.format, len(df))

    except Exception as exc:
        logger.error("Export hatası (job=%s): %s", job_id, exc)
        job.status = ExportJob.FAILED
        job.error_message = str(exc)
        job.save(update_fields=["status", "error_message"])
        raise self.retry(exc=exc)


@shared_task
def cleanup_expired_export_jobs() -> None:
    """
    Süresi dolmuş (expires_at geçmiş) export işlerini ve dosyalarını temizler.
    Beat: her gün 03:00.
    """
    from django.utils.timezone import now

    from apps.exports.models import ExportJob

    expired = ExportJob.objects.filter(status=ExportJob.COMPLETE, expires_at__lt=now())
    count = 0
    for job in expired:
        if job.file_path and os.path.exists(job.file_path):
            try:
                os.remove(job.file_path)
            except OSError as exc:
                logger.warning("Export dosyası silinemedi (%s): %s", job.file_path, exc)
        job.delete()
        count += 1

    logger.info("Süresi dolmuş %d export işi temizlendi.", count)


def _query_sensor_data(filters: dict, user_id: int):
    """
    Filtrelere göre sensor_readings'i çeker ve DataFrame döndürür.
    Kullanıcının üye olduğu çiftliklerle sınırlıdır (güvenlik).
    """
    import pandas as pd
    from django.db import connection

    where_clauses = [
        "sr.device_id IN ("
        "  SELECT d.id FROM devices d"
        "  JOIN farm_memberships fm ON fm.farm_id = d.farm_id"
        "  WHERE fm.user_id = %s"
        ")"
    ]
    params = [user_id]

    if filters.get("device_id"):
        where_clauses.append("sr.device_id = %s")
        params.append(filters["device_id"])
    if filters.get("capability"):
        where_clauses.append("sr.capability_type = %s")
        params.append(filters["capability"])
    if filters.get("start"):
        where_clauses.append("sr.time >= %s")
        params.append(filters["start"])
    if filters.get("end"):
        where_clauses.append("sr.time <= %s")
        params.append(filters["end"])

    where_sql = " AND ".join(where_clauses)
    sql = f"""
        SELECT
            sr.time,
            d.device_uid,
            d.name AS device_name,
            sr.capability_type,
            sr.value
        FROM sensor_readings sr
        JOIN devices d ON d.id = sr.device_id
        WHERE {where_sql}
        ORDER BY sr.time DESC
    """
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()

    return pd.DataFrame(rows, columns=columns)
