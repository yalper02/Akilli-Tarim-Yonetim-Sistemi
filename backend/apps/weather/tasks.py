"""
Hava durumu Celery görevleri.
"""

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(ignore_result=True)
def fetch_weather_for_all_farms() -> None:
    """Tüm aktif çiftliklerin hava durumu önbelleğini yeniler (saatlik Beat görevi)."""
    from apps.farms.models import Farm
    from apps.weather.services import refresh_weather_cache

    farms = Farm.objects.filter(latitude__isnull=False, longitude__isnull=False)
    total = farms.count()
    success = 0

    for farm in farms:
        try:
            if refresh_weather_cache(farm) is not None:
                success += 1
        except Exception as exc:
            logger.error("Hava durumu yenileme hatası: farm_id=%s hata=%s", farm.pk, exc)

    logger.info("Hava durumu yenilendi: %s/%s çiftlik", success, total)
