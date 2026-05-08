"""
Cihaz izleme Celery görevi — çevrimdışı cihazları tespit eder ve bildirir.
"""

import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(ignore_result=True)
def check_offline_devices() -> None:
    """
    Son 1 saatte telemetri almayan ONLINE cihazları OFFLINE işaretler,
    çiftlik üyelerine bildirim gönderir (her geçiş için tek bildirim).
    """
    from apps.accounts.models import FarmMembership
    from apps.devices.models import Device
    from apps.notifications.models import Notification

    cutoff = timezone.now() - timedelta(hours=1)

    # last_seen_at NULL olan (hiç veri gelmeyen) cihazlar bu filtreden çıkar
    stale_devices = Device.objects.filter(
        status=Device.ONLINE,
        last_seen_at__lt=cutoff,
    ).select_related("farm")

    for device in stale_devices:
        device.status = Device.OFFLINE
        device.save(update_fields=["status"])
        logger.warning(
            "Cihaz çevrimdışı: device=%s farm_id=%s last_seen=%s",
            device.device_uid,
            device.farm_id,
            device.last_seen_at,
        )

        # Çiftlik üyelerine toplu bildirim oluştur
        memberships = FarmMembership.objects.filter(farm=device.farm).select_related("user")
        notifications = [
            Notification(
                user=m.user,
                farm=device.farm,
                title=f"Cihaz Çevrimdışı: {device.name}",
                message=(
                    f"{device.name} ({device.device_uid}) adlı cihazdan "
                    f"son 1 saattir veri alınamıyor. Lütfen cihazı kontrol edin."
                ),
                notification_type="device_offline",
                severity=Notification.WARNING,
                related_object_type="device",
                related_object_id=device.pk,
            )
            for m in memberships
        ]
        if notifications:
            Notification.objects.bulk_create(notifications)
            logger.info(
                "%s üyeye çevrimdışı bildirimi gönderildi: device=%s",
                len(notifications),
                device.device_uid,
            )
