"""
Denetim günlüğü yazma yardımcısı.
"""

import logging

from django.utils import timezone

logger = logging.getLogger(__name__)


def write_audit_log(
    action_type: str,
    resource_type: str = "",
    resource_id: int | None = None,
    details: dict | None = None,
    user=None,
    ip_address: str | None = None,
) -> None:
    """
    audit_logs hypertable'ına kayıt ekler.
    Hata durumunda ana iş akışını kesmez — sadece log yazar.
    """
    from apps.audit.models import AuditLog

    try:
        AuditLog.objects.create(
            time=timezone.now(),
            user=user,
            ip_address=ip_address,
            action_type=action_type,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
        )
    except Exception as exc:
        logger.error("Denetim günlüğü yazılamadı (action=%s): %s", action_type, exc)
