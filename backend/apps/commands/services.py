"""
Komut yayıncısı — Command kaydı oluşturur ve MQTT broker'a gönderir.
"""

import json
import logging
import os
import ssl

import paho.mqtt.client as mqtt

from apps.commands.models import Command

logger = logging.getLogger(__name__)

MQTT_HOST = os.environ.get("MQTT_BROKER_HOST", "localhost")
MQTT_PORT = int(os.environ.get("MQTT_BROKER_PORT", "8883"))
MQTT_USER = os.environ.get("MQTT_BACKEND_USER", "backend")
MQTT_PASS = os.environ.get("MQTT_BACKEND_PASSWORD", "change-me-backend-password")
MQTT_TLS_CA = os.environ.get("MQTT_TLS_CA_CERT", "")


def _publish_mqtt(topic: str, payload: dict, qos: int = 2) -> bool:
    """
    Tek bir MQTT mesajı yayınlar, bağlantıyı kapatır.
    Başarıysa True, hata durumunda False döner.
    """
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.username_pw_set(MQTT_USER, MQTT_PASS)

    if MQTT_TLS_CA:
        client.tls_set(ca_certs=MQTT_TLS_CA, tls_version=ssl.PROTOCOL_TLS_CLIENT)
    else:
        # Geliştirme ortamı: self-signed sertifika doğrulaması atlanır
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        client.tls_set_context(ctx)

    try:
        client.connect(MQTT_HOST, MQTT_PORT, keepalive=30)
        client.loop_start()
        info = client.publish(topic, json.dumps(payload), qos=qos)
        info.wait_for_publish(timeout=5.0)
        logger.debug("MQTT mesajı yayınlandı: topic=%s", topic)
        return True
    except Exception as exc:
        logger.error("MQTT yayın hatası (topic=%s): %s", topic, exc)
        return False
    finally:
        client.loop_stop()
        try:
            client.disconnect()
        except Exception:
            pass


def publish_command(
    device,
    action_type: str,
    parameters: dict | None = None,
    rule=None,
    user=None,
) -> Command:
    """
    Command kaydı oluşturur ve ilgili cihaz topic'ine MQTT komutu gönderir.
    rule veya user'dan tam olarak biri verilmeli (commands CHECK constraint).
    Gönderim başarısızsa command.status FAILED olarak güncellenir.
    """
    from django.utils.timezone import now

    triggered_by = Command.AUTOMATIC if rule is not None else Command.MANUAL
    cmd = Command.objects.create(
        device=device,
        rule=rule,
        user=user,
        action_type=action_type,
        parameters=parameters or {},
        triggered_by=triggered_by,
        status=Command.PENDING,
    )

    topic = f"farms/{device.farm_id}/devices/{device.device_uid}/commands"
    payload = {
        "command_id": str(cmd.command_uid),
        "action": action_type,
        "issued_at": now().isoformat(),
        **(parameters or {}),
    }
    if rule is not None:
        payload["issued_by"] = f"rule-{rule.pk}"
    elif user is not None:
        payload["issued_by"] = f"user-{user.pk}"

    success = _publish_mqtt(topic, payload)
    if not success:
        cmd.status = Command.FAILED
        cmd.save(update_fields=["status"])
        logger.error(
            "Komut MQTT'ye gönderilemedi: cmd_uid=%s device=%s",
            cmd.command_uid,
            device.device_uid,
        )

    return cmd
