"""
Bildirim e-posta görevi — Celery üzerinden SMTP ile iletir.
"""

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_notification_email(self, notification_id: int) -> None:
    """
    Belirtilen bildirimi kullanıcının e-posta adresine gönderir.
    SMTP hatasında Celery retry mekanizması devreye girer (max 3 deneme).
    """
    from django.conf import settings
    from django.core.mail import send_mail

    from apps.notifications.models import Notification

    try:
        notif = Notification.objects.select_related("user").get(pk=notification_id)
    except Notification.DoesNotExist:
        logger.warning("E-posta için bildirim bulunamadı: id=%s", notification_id)
        return

    if not notif.user.email:
        logger.debug("Kullanıcının e-posta adresi yok: user=%s", notif.user.username)
        return

    try:
        send_mail(
            subject=notif.title,
            message=notif.message,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"),
            recipient_list=[notif.user.email],
            fail_silently=False,
        )
        logger.info(
            "Bildirim e-postası gönderildi: notification=%s → %s",
            notification_id,
            notif.user.email,
        )
    except Exception as exc:
        logger.error("E-posta gönderilemedi (notification=%s): %s", notification_id, exc)
        raise self.retry(exc=exc)
