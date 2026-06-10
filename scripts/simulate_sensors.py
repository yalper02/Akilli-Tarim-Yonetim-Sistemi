import time
import json
import random
import os
import sys
import django
import paho.mqtt.client as mqtt

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from visualization.models import Parcel, SensorData

# Konfigürasyon
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "atys/telemetry/"

def on_connect(client, userdata, flags, reason_code, properties=None):
    print(f"✅ Simülatör MQTT Broker'a bağlandı. (Kod: {reason_code})")

def simulate():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    
    # Başlangıç değerleri (Veritabanındaki aktif parsellere göre dinamik oluşturulur)
    parcels = Parcel.objects.filter(is_active=True)
    if not parcels.exists():
        print("Sistemde aktif parsel yok! Device_01, Device_02 ve Device_03 varsayılan olarak ekleniyor...")
        Parcel.objects.create(name="Device_01")
        Parcel.objects.create(name="Device_02")
        Parcel.objects.create(name="Device_03")
        parcels = Parcel.objects.filter(is_active=True)

    devices = []
    for p in parcels:
        last_data = SensorData.objects.filter(parcel=p).order_by('-timestamp').first()
        devices.append({
            "id": p.name,
            "temp": last_data.temperature if last_data else random.uniform(20.0, 30.0),
            "moist": last_data.soil_moisture if last_data else random.uniform(40.0, 60.0),
            "battery": last_data.battery_level if last_data and last_data.battery_level else random.uniform(80.0, 100.0),
            "rssi": last_data.rssi if last_data and last_data.rssi else random.uniform(-70, -40)
        })

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
        
        print("🚀 Dinamik Sensör Simülatörü Başlatıldı! (SADECE OKUMA MODU)")
        
        while True:
            for dev in devices:
                # Sadece Okuma (Read-Only) Modu: Veritabanına ASLA müdahale etmez (save() kullanılamaz)
                try:
                    # Yeni bir instance almak yerine veritabanından sadece durumu sorguluyoruz
                    is_irrigating = Parcel.objects.filter(name=dev["id"]).values_list('is_irrigating', flat=True).first()
                except:
                    is_irrigating = False

                if is_irrigating:
                    dev["moist"] += 0.8
                    print(f"💦 Pompa Çalışıyor! {dev['id']} Nem artıyor: {dev['moist']:.1f}%")
                else:
                    dev["moist"] -= random.uniform(-0.2, 0.5)
                
                dev["temp"] += random.uniform(-0.5, 0.5)
                
                # Sınırları koru
                dev["temp"] = max(-10, min(50, dev["temp"]))
                dev["moist"] = max(0, min(100, dev["moist"]))
                dev["battery"] = max(0, dev["battery"] - random.uniform(0.01, 0.05))
                dev["rssi"] = int(random.uniform(-80, -40))

                payload = {
                    "device_id": dev["id"],
                    "temperature": round(dev["temp"], 1),
                    "soil_moisture": round(dev["moist"], 1),
                    "battery_level": round(dev["battery"], 1),
                    "rssi": dev["rssi"],
                    "humidity": int(random.uniform(40, 60))
                }
                
                topic = f"{MQTT_TOPIC}{dev['id']}"
                client.publish(topic, json.dumps(payload))
                print(f"📡 Gönderildi -> {dev['id']}: Temp={payload['temperature']}°C, Moist={payload['soil_moisture']}%")
            
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\n🛑 Simülatör durduruldu.")
        client.loop_stop()
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    simulate()
