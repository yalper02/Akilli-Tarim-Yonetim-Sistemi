"""
MQTT Worker — Mosquitto'ya abone olur, gelen telemetri mesajlarını işler,
sensor_readings ve device_telemetry hypertable'larına yazar.
django.setup() ile Django ORM'i başlatır; bağımsız proses olarak çalışır.
"""

import json
import logging
import os
import ssl
import uuid

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

import paho.mqtt.client as mqtt  # noqa: E402 — django.setup() sonrası import

from apps.mqtt_worker.validator import validate_message  # noqa: E402

logger = logging.getLogger(__name__)

MQTT_HOST = os.environ.get("MQTT_BROKER_HOST", "localhost")
MQTT_PORT = int(os.environ.get("MQTT_BROKER_PORT", "8883"))
MQTT_USER = os.environ.get("MQTT_BACKEND_USER", "backend")
MQTT_PASS = os.environ.get("MQTT_BACKEND_PASSWORD", "change-me-backend-password")
MQTT_TLS_CA = os.environ.get("MQTT_TLS_CA_CERT", "")


def _broadcast_reading(device, capability_type: str, value: float, ts) -> None:
    """Sensör okumasını çiftlik WebSocket grubuna yayınlar."""
    try:
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer

        channel_layer = get_channel_layer()
        if channel_layer is None:
            return

        async_to_sync(channel_layer.group_send)(
            f"farm-{device.farm_id}",
            {
                "type": "sensor_reading",
                "data": {
                    "device_id": device.id,
                    "device_uid": device.device_uid,
                    "capability_type": capability_type,
                    "value": value,
                    "time": ts.isoformat(),
                },
            },
        )
    except Exception as exc:
        logger.warning("WebSocket yayını başarısız (farm=%s): %s", device.farm_id, exc)


def _parse_topic(topic: str) -> tuple[str | None, str | None]:
    """'farms/{farm_id}/devices/{device_uid}/...' → (farm_id, device_uid)"""
    parts = topic.split("/")
    if len(parts) >= 4 and parts[0] == "farms" and parts[2] == "devices":
        return parts[1], parts[3]
    return None, None


def _handle_telemetry(device_uid: str, payload: dict) -> None:
    """Telemetri mesajını doğrular, DB'ye yazar, kural motorunu tetikler."""
    from django.utils import timezone

    from apps.devices.models import Device
    from apps.rules.tasks import evaluate_rules_task
    from apps.sensor_data.models import DeviceTelemetry, SensorReading

    ts, readings, telemetry = validate_message(payload)
    if ts is None:
        return

    try:
        device = Device.objects.get(device_uid=device_uid)
    except Device.DoesNotExist:
        logger.warning("Bilinmeyen cihaz, mesaj reddedildi: %s", device_uid)
        return

    for capability_type, value in readings.items():
        reading = SensorReading.objects.create(
            time=ts,
            device=device,
            capability_type=capability_type,
            value=value,
        )
        logger.info(
            "Okuma kaydedildi: device=%s capability=%s value=%.2f",
            device_uid,
            capability_type,
            value,
        )
        try:
            evaluate_rules_task.delay(reading.pk)
        except Exception as exc:
            logger.warning("Celery görevi kuyruğa alınamadı (reading=%s): %s", reading.pk, exc)

        # Canlı dashboard için WebSocket grubuna yayınla
        _broadcast_reading(device, capability_type, value, ts)

    if telemetry:
        DeviceTelemetry.objects.create(
            time=ts,
            device=device,
            battery_level=telemetry.get("battery_level"),
            rssi=telemetry.get("rssi"),
        )

    device.last_seen_at = timezone.now()
    device.status = Device.ONLINE
    device.save(update_fields=["last_seen_at", "status"])


def _handle_status(device_uid: str, payload: dict) -> None:
    """Cihaz online/offline durum güncellemesi (LWT dahil)."""
    from apps.devices.models import Device

    status_str = payload.get("status", "")
    new_status = Device.ONLINE if status_str == "online" else Device.OFFLINE
    updated = Device.objects.filter(device_uid=device_uid).update(status=new_status)
    if updated:
        logger.info("Cihaz durumu güncellendi: %s → %s", device_uid, new_status)
    else:
        logger.warning("Durum güncellemesi için bilinmeyen cihaz: %s", device_uid)


def _handle_ack(device_uid: str, payload: dict) -> None:
    """Komut ACK'ini işler, commands tablosunu günceller."""
    from django.utils import timezone

    from apps.commands.models import Command

    raw_uid = payload.get("command_id", "")
    status = payload.get("status", "")
    if not raw_uid or not status:
        return

    try:
        cmd_uuid = uuid.UUID(str(raw_uid))
    except ValueError:
        logger.warning("Geçersiz command_id formatı: %s", raw_uid)
        return

    update_fields: dict = {"status": status}
    if status == Command.EXECUTED:
        update_fields["executed_at"] = timezone.now()

    updated = Command.objects.filter(command_uid=cmd_uuid).update(**update_fields)
    if updated:
        logger.info("Komut onaylandı: %s → %s", raw_uid, status)
    else:
        logger.warning("ACK için bilinmeyen komut: %s", raw_uid)


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        logger.info("Mosquitto'ya bağlandı: %s:%s", MQTT_HOST, MQTT_PORT)
        client.subscribe("farms/+/devices/+/telemetry", qos=1)
        client.subscribe("farms/+/devices/+/status", qos=1)
        client.subscribe("farms/+/devices/+/commands/ack", qos=2)
    else:
        logger.error("Bağlantı reddedildi: reason_code=%s", reason_code)


def on_disconnect(client, userdata, flags, reason_code, properties):
    if reason_code != 0:
        logger.warning("Beklenmedik bağlantı kopması: reason_code=%s", reason_code)


def on_message(client, userdata, msg):
    topic = msg.topic
    try:
        payload = json.loads(msg.payload.decode())
    except (json.JSONDecodeError, UnicodeDecodeError):
        logger.warning("JSON parse hatası: topic=%s", topic)
        return

    _, device_uid = _parse_topic(topic)
    if not device_uid:
        return

    if topic.endswith("/telemetry"):
        _handle_telemetry(device_uid, payload)
    elif topic.endswith("/status"):
        _handle_status(device_uid, payload)
    elif topic.endswith("/commands/ack"):
        _handle_ack(device_uid, payload)


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(asctime)s %(name)s %(message)s",
    )

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.username_pw_set(MQTT_USER, MQTT_PASS)

    if MQTT_TLS_CA:
        client.tls_set(ca_certs=MQTT_TLS_CA, tls_version=ssl.PROTOCOL_TLS_CLIENT)
    else:
        # CA sertifikası yoksa geliştirme modunda doğrulama atlanır
        client.tls_set(cert_reqs=ssl.CERT_NONE, tls_version=ssl.PROTOCOL_TLS_CLIENT)
        client.tls_insecure_set(True)

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    logger.info("Mosquitto'ya bağlanılıyor: %s:%s", MQTT_HOST, MQTT_PORT)
    client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
    client.loop_forever()


if __name__ == "__main__":
    main()
