"""
Sensör simülatörü — config.yaml'dan cihaz listesini okur,
belirtilen aralıkta MQTT üzerinden telemetri yayınlar.
Nem drift simülasyonu: valf kapalıysa nem her döngüde azalır.
Aktüatörler komut topic'ine abone olur ve ACK yayınlar.
"""
import json
import logging
import os
import random
import ssl
import time
from datetime import datetime, timezone
from pathlib import Path

import paho.mqtt.client as mqtt
import yaml

logger = logging.getLogger(__name__)

CONFIG_PATH = Path(__file__).parent / "config.yaml"


class DeviceSimulator:
    """Tek bir cihazın yaşam döngüsünü ve telemetri simülasyonunu yönetir."""

    def __init__(
        self,
        farm_id: int,
        device_cfg: dict,
        mqtt_cfg: dict,
        ca_cert_override: str = "",
    ):
        self.farm_id = farm_id
        self.device_uid = device_cfg["device_uid"]
        self.device_type = device_cfg.get("device_type", "sensor")
        self.capabilities: dict = device_cfg.get("capabilities", {})
        self.telemetry_cfg: dict = device_cfg.get("telemetry", {})

        # Her capability için başlangıç değerini base'den al
        self.state: dict[str, float] = {
            cap: float(cfg.get("base", 0.0)) for cap, cfg in self.capabilities.items()
        }
        self.battery = float(
            self.telemetry_cfg.get("battery_level", {}).get("base", 100.0)
        )
        self.rssi_base = float(self.telemetry_cfg.get("rssi", {}).get("base", -70.0))

        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=f"sim-{self.device_uid}",
        )
        self.client.username_pw_set(device_cfg["username"], device_cfg["password"])
        self._configure_tls(mqtt_cfg, ca_cert_override)
        self._configure_lwt()
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message

    def _configure_tls(self, mqtt_cfg: dict, ca_cert_override: str = "") -> None:
        # Env var > config.yaml > yok (güvensiz mod)
        ca_cert = ca_cert_override or mqtt_cfg.get("ca_cert", "")
        if ca_cert:
            # Mutlak yol veya config dosyasına göre relatif yol
            ca_path = Path(ca_cert) if Path(ca_cert).is_absolute() else (CONFIG_PATH.parent / ca_cert).resolve()
        else:
            ca_path = None

        if ca_path and ca_path.exists():
            self.client.tls_set(
                ca_certs=str(ca_path), tls_version=ssl.PROTOCOL_TLS_CLIENT
            )
        else:
            # CA sertifikası yoksa geliştirme modunda doğrulama atlanır
            self.client.tls_set(
                cert_reqs=ssl.CERT_NONE, tls_version=ssl.PROTOCOL_TLS_CLIENT
            )
            self.client.tls_insecure_set(True)

    def _configure_lwt(self) -> None:
        """LWT: beklenmedik kopuşta broker "offline" yayınlar (retained)."""
        topic = f"farms/{self.farm_id}/devices/{self.device_uid}/status"
        self.client.will_set(
            topic, json.dumps({"status": "offline"}), qos=1, retain=True
        )

    def _on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code != 0:
            logger.error("[%s] Bağlantı hatası: %s", self.device_uid, reason_code)
            return

        logger.info("[%s] Bağlandı", self.device_uid)
        # Çevrimiçi durum yayınla
        status_topic = f"farms/{self.farm_id}/devices/{self.device_uid}/status"
        client.publish(
            status_topic, json.dumps({"status": "online"}), qos=1, retain=True
        )
        # Aktüatörler komut topic'ine abone olur
        if self.device_type in ("actuator", "combined"):
            cmd_topic = f"farms/{self.farm_id}/devices/{self.device_uid}/commands"
            client.subscribe(cmd_topic, qos=2)
            logger.info("[%s] Komut topic'ine abone olundu", self.device_uid)

    def _on_disconnect(self, client, userdata, flags, reason_code, properties):
        if reason_code != 0:
            logger.warning("[%s] Beklenmedik kopma: %s", self.device_uid, reason_code)

    def _on_message(self, client, userdata, msg):
        """Gelen komut mesajını işler ve ACK yayınlar."""
        try:
            payload = json.loads(msg.payload.decode())
        except (json.JSONDecodeError, UnicodeDecodeError):
            return

        command_id = payload.get("command_id", "")
        action = payload.get("action", "")
        logger.info("[%s] Komut alındı: action=%s", self.device_uid, action)

        # Simüle edilmiş yürütme gecikmesi (0.5–2 saniye)
        time.sleep(random.uniform(0.5, 2.0))

        ack_topic = f"farms/{self.farm_id}/devices/{self.device_uid}/commands/ack"
        ack = {
            "command_id": command_id,
            "status": "executed",
            "executed_at": datetime.now(timezone.utc)
            .isoformat()
            .replace("+00:00", "Z"),
        }
        client.publish(ack_topic, json.dumps(ack), qos=2)
        logger.info("[%s] ACK yayınlandı: %s", self.device_uid, command_id)

    def _advance_state(self) -> dict[str, float]:
        """Her capability için bir sonraki değeri hesaplar (drift + gürültü)."""
        for cap, cfg in self.capabilities.items():
            drift = float(cfg.get("drift", 0.0))
            noise = float(cfg.get("noise", 0.0))
            lo = float(cfg.get("min", 0.0))
            hi = float(cfg.get("max", 100.0))
            self.state[cap] = max(
                lo,
                min(hi, self.state[cap] + drift + random.uniform(-noise, noise)),
            )
        return self.state

    def publish_telemetry(self) -> None:
        """Anlık telemetri mesajı oluşturup yayınlar."""
        if not self.capabilities:
            return  # Aktüatörün yayınlayacak sensör okuma verisi yok

        readings = {cap: round(v, 2) for cap, v in self._advance_state().items()}

        bat_drift = float(self.telemetry_cfg.get("battery_level", {}).get("drift", 0))
        self.battery = max(0.0, self.battery + bat_drift)
        rssi_noise = float(self.telemetry_cfg.get("rssi", {}).get("noise", 0))

        message = {
            "timestamp": datetime.now(timezone.utc)
            .isoformat()
            .replace("+00:00", "Z"),
            "device_id": self.device_uid,
            "readings": readings,
            "telemetry": {
                "battery_level": round(self.battery),
                "rssi": round(
                    self.rssi_base + random.uniform(-rssi_noise, rssi_noise)
                ),
            },
        }

        topic = f"farms/{self.farm_id}/devices/{self.device_uid}/telemetry"
        self.client.publish(topic, json.dumps(message), qos=1)
        logger.info("[%s] Telemetri: %s", self.device_uid, readings)

    def connect(self, host: str, port: int) -> None:
        self.client.connect_async(host, port, keepalive=60)
        self.client.loop_start()

    def disconnect(self) -> None:
        """Temiz kopuş: "offline" yayınla, sonra bağlantıyı kes."""
        status_topic = f"farms/{self.farm_id}/devices/{self.device_uid}/status"
        self.client.publish(
            status_topic, json.dumps({"status": "offline"}), qos=1, retain=True
        )
        time.sleep(0.3)
        self.client.loop_stop()
        self.client.disconnect()


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(asctime)s %(message)s",
    )

    with open(CONFIG_PATH) as f:
        config = yaml.safe_load(f)

    mqtt_cfg: dict = config["mqtt"]
    # Docker ortamında env var'lar config.yaml değerlerini ezer
    host: str = os.environ.get("MQTT_HOST") or mqtt_cfg.get("host", "localhost")
    port: int = int(os.environ.get("MQTT_PORT") or mqtt_cfg.get("port", 8883))
    ca_cert: str = os.environ.get("MQTT_CA_CERT", "")
    interval: int = int(config.get("publish_interval_seconds", 30))

    simulators: list[DeviceSimulator] = []
    for farm in config.get("farms", []):
        for device_cfg in farm.get("devices", []):
            sim = DeviceSimulator(farm["farm_id"], device_cfg, mqtt_cfg, ca_cert_override=ca_cert)
            sim.connect(host, port)
            simulators.append(sim)

    logger.info(
        "%d cihaz başlatıldı — %ds aralıkla telemetri yayını yapılıyor",
        len(simulators),
        interval,
    )

    try:
        time.sleep(2)  # Bağlantıların kurulması için kısa bekleme
        while True:
            for sim in simulators:
                sim.publish_telemetry()
            time.sleep(interval)
    except KeyboardInterrupt:
        logger.info("Simülatör durduruluyor...")
    finally:
        for sim in simulators:
            sim.disconnect()


if __name__ == "__main__":
    main()
