"""
Bildirim yardımcı servisi — bildirim oluşturur ve WebSocket üzerinden kullanıcıya iletir.
"""

import logging

from .models import Notification

logger = logging.getLogger(__name__)


def create_notification(
    user,
    title: str,
    message: str,
    notification_type: str,
    severity: str = Notification.INFO,
    farm=None,
    related_object_type: str = "",
    related_object_id=None,
) -> Notification:
    """Bildirim kaydı oluşturur; WebSocket kanalına broadcast eder."""
    notif = Notification.objects.create(
        user=user,
        farm=farm,
        title=title,
        message=message,
        notification_type=notification_type,
        severity=severity,
        related_object_type=related_object_type,
        related_object_id=related_object_id,
    )
    _broadcast(notif)
    return notif


def _broadcast(notif: Notification) -> None:
    """Kullanıcının WebSocket grubuna bildirim mesajı gönder."""
    try:
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer

        channel_layer = get_channel_layer()
        if channel_layer is None:
            return

        async_to_sync(channel_layer.group_send)(
            f"user-{notif.user_id}",
            {
                "type": "notification",
                "data": {
                    "id": notif.id,
                    "title": notif.title,
                    "message": notif.message,
                    "notification_type": notif.notification_type,
                    "severity": notif.severity,
                    "is_read": notif.is_read,
                    "created_at": notif.created_at.isoformat(),
                },
            },
        )
    except Exception as exc:
        logger.warning("WebSocket bildirim yayını başarısız: %s", exc)
