"""
NFR-04 kapsamında gelen MQTT mesajlarının fiziksel ve zamansal doğrulaması.
"""

import logging
from datetime import UTC, datetime, timedelta

logger = logging.getLogger(__name__)

# Kabul edilebilir sensör değer aralıkları
CAPABILITY_RANGES: dict[str, tuple[float, float]] = {
    "soil_moisture": (0.0, 100.0),
    "temperature": (-50.0, 80.0),
    "humidity": (0.0, 100.0),
    "ph_level": (0.0, 14.0),
    "nitrogen_level": (0.0, 10_000.0),
    "phosphorus_level": (0.0, 10_000.0),
    "potassium_level": (0.0, 10_000.0),
}

# Maksimum veri yaşı ve gelecek toleransı
MAX_AGE_HOURS = 24
MAX_FUTURE_SECONDS = 60


def validate_timestamp(ts_str: str) -> datetime | None:
    """ISO 8601 timestamp'i parse eder, geçerlilik aralığını kontrol eder."""
    try:
        ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        logger.warning("Geçersiz timestamp formatı reddedildi: %s", ts_str)
        return None

    now = datetime.now(UTC)

    if ts > now + timedelta(seconds=MAX_FUTURE_SECONDS):
        logger.warning("Gelecek zamanlı veri reddedildi: %s", ts_str)
        return None

    if ts < now - timedelta(hours=MAX_AGE_HOURS):
        logger.warning("24 saatten eski veri reddedildi: %s", ts_str)
        return None

    return ts


def validate_readings(readings: dict) -> dict[str, float]:
    """
    Readings dict'ini doğrular.
    Bilinmeyen capability ve fiziksel aralık dışı değerler çıkarılır.
    """
    valid: dict[str, float] = {}
    for capability, raw_value in readings.items():
        if capability not in CAPABILITY_RANGES:
            logger.debug("Bilinmeyen capability atlandı: %s", capability)
            continue
        try:
            value = float(raw_value)
        except (TypeError, ValueError):
            logger.warning("Sayısal olmayan değer reddedildi: %s=%s", capability, raw_value)
            continue
        lo, hi = CAPABILITY_RANGES[capability]
        if not (lo <= value <= hi):
            logger.warning(
                "Fiziksel aralık dışı değer reddedildi: %s=%.2f (beklenen: %.1f–%.1f)",
                capability,
                value,
                lo,
                hi,
            )
            continue
        valid[capability] = value
    return valid


def validate_battery(raw: int | float | None) -> int | None:
    """Batarya seviyesi 0–100 arasında olmalı."""
    if raw is None:
        return None
    try:
        val = int(float(raw))
        return val if 0 <= val <= 100 else None
    except (TypeError, ValueError):
        return None


def validate_rssi(raw: int | float | None) -> int | None:
    """RSSI değeri -120 ile 0 dBm arasında olmalı."""
    if raw is None:
        return None
    try:
        val = int(float(raw))
        return val if -120 <= val <= 0 else None
    except (TypeError, ValueError):
        return None


def validate_message(
    payload: dict,
) -> tuple[datetime | None, dict[str, float], dict[str, int]]:
    """
    Ham MQTT telemetri mesajını doğrular.

    Döndürür: (timestamp, valid_readings, valid_telemetry)
    timestamp None ise mesaj tamamen reddedilmeli.
    """
    ts = validate_timestamp(payload.get("timestamp", ""))
    if ts is None:
        return None, {}, {}

    readings = validate_readings(payload.get("readings", {}))

    raw_tel = payload.get("telemetry", {})
    telemetry: dict[str, int] = {}

    battery = validate_battery(raw_tel.get("battery_level"))
    if battery is not None:
        telemetry["battery_level"] = battery

    rssi = validate_rssi(raw_tel.get("rssi"))
    if rssi is not None:
        telemetry["rssi"] = rssi

    return ts, readings, telemetry
