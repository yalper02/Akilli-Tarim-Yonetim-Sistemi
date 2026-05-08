"""
Open-Meteo hava durumu servisi — Redis cache + WeatherCache DB fallback.
"""

import logging
from datetime import UTC, datetime, timedelta

import requests
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

logger = logging.getLogger(__name__)

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
_CACHE_KEY_PREFIX = "weather:farm:"


def _cache_key(farm_id: int) -> str:
    return f"{_CACHE_KEY_PREFIX}{farm_id}"


def _fetch_from_open_meteo(latitude: float, longitude: float) -> dict | None:
    """Open-Meteo API'sinden saatlik yağış olasılığı tahminini çeker."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "precipitation_probability",
        "forecast_days": 2,
        "timezone": "UTC",
    }
    try:
        response = requests.get(OPEN_METEO_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        logger.warning("Open-Meteo isteği başarısız: %s", exc)
        return None


def refresh_weather_cache(farm) -> dict | None:
    """
    Çiftlik için hava durumu verisini Open-Meteo'dan çeker,
    Redis ve WeatherCache tablosuna kaydeder.
    Koordinat eksikse veya istek başarısızsa None döner.
    """
    from apps.weather.models import WeatherCache

    if farm.latitude is None or farm.longitude is None:
        logger.debug("Çiftlik koordinatı yok, hava durumu atlandı: farm_id=%s", farm.pk)
        return None

    data = _fetch_from_open_meteo(farm.latitude, farm.longitude)
    if data is None:
        return None

    ttl = getattr(settings, "WEATHER_CACHE_TTL_SECONDS", 3600)
    cache.set(_cache_key(farm.pk), data, timeout=ttl)

    # DB'ye yaz — eski kayıt varsa sil, yenisini oluştur (fetched_at taze kalsın)
    valid_until = timezone.now() + timedelta(seconds=ttl)
    WeatherCache.objects.filter(farm=farm).delete()
    WeatherCache.objects.create(farm=farm, forecast_data=data, valid_until=valid_until)

    logger.info("Hava durumu önbelleğe alındı: farm_id=%s", farm.pk)
    return data


def get_weather_forecast(farm) -> dict | None:
    """
    Çiftlik için hava durumu tahminini döner.
    Önce Redis, yoksa Open-Meteo, yoksa DB'deki son kayıt (eski de olsa).
    """
    from apps.weather.models import WeatherCache

    # 1. Redis cache — en hızlı yol
    data = cache.get(_cache_key(farm.pk))
    if data is not None:
        return data

    # 2. Open-Meteo'dan taze veri çek + Redis + DB'ye kaydet
    data = refresh_weather_cache(farm)
    if data is not None:
        return data

    # 3. DB fallback — geçerliliği dolmuş olsa bile son kaydı kullan
    cached = WeatherCache.objects.filter(farm=farm).order_by("-fetched_at").first()
    if cached:
        logger.warning(
            "Eski DB kaydından hava durumu kullanılıyor: farm_id=%s fetched_at=%s",
            farm.pk,
            cached.fetched_at,
        )
        return cached.forecast_data

    return None


def get_max_rain_probability(farm, hours_ahead: int = 24) -> int | None:
    """
    Önümüzdeki hours_ahead saat içindeki maksimum yağış olasılığını döner (0–100).
    Hava durumu verisi alınamazsa None döner.
    """
    forecast = get_weather_forecast(farm)
    if not forecast:
        return None

    hourly = forecast.get("hourly", {})
    times = hourly.get("time", [])
    probs = hourly.get("precipitation_probability", [])

    now = timezone.now()
    cutoff = now + timedelta(hours=hours_ahead)
    max_prob = 0

    for time_str, prob in zip(times, probs):
        if prob is None:
            continue
        # Open-Meteo UTC formatı: "2026-05-01T00:00" → timezone-aware datetime
        t = datetime.fromisoformat(time_str).replace(tzinfo=UTC)
        if now <= t <= cutoff:
            max_prob = max(max_prob, int(prob))

    return max_prob
