import os
import sys
import json
import time
import django
import asyncio
from datetime import timedelta
from asgiref.sync import sync_to_async
import paho.mqtt.client as mqtt

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.utils import timezone
from visualization.models import Parcel, SensorData
from scripts.telegram_bot import send_alert

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "atys/telemetry/#"

def validate_data(temp, moist, battery):
    # NFR-04: Discard nonsensical values
    if temp < -50 or temp > 80:
        return False
    if moist < 0 or moist > 100:
        return False
    if battery < 0 or battery > 100:
        return False
    return True

@sync_to_async
def get_active_parcels():
    return list(Parcel.objects.filter(is_active=True))

@sync_to_async
def get_last_sensor_data(parcel):
    return SensorData.objects.filter(parcel=parcel).order_by('-timestamp').first()

@sync_to_async
def save_telemetry_data(device_id, temp, moist, battery, rssi, humidity):
    parcel, created = Parcel.objects.get_or_create(name=device_id)
    
    # Güvenlik Protokolü: Nem %85'e ulaştığında pompayı kapat (Worker tarafında yapılmalı)
    if parcel.is_irrigating and moist >= 85.0:
        parcel.is_irrigating = False
        print(f"🛑 Güvenlik Protokolü: {parcel.name} nemi %85'e ulaştı, pompa durduruldu!")
        # Uyarıyı activity log'a da yazabiliriz
        ActivityLog.objects.create(
            event_type='INFO',
            description=f'Otomatik Kapatma: {parcel.name} nem oranı %{moist} seviyesine ulaştığı için sulama durduruldu.'
        )

    SensorData.objects.create(
        parcel=parcel,
        device_name=device_id,
        temperature=temp,
        humidity=humidity,
        soil_moisture=moist,
        battery_level=battery,
        rssi=rssi
    )

    parcel.last_moisture = moist
    parcel.battery_level = battery
    parcel.rssi = rssi
    parcel.save()
    
    return parcel

async def check_alerts(parcel, temp, moist, battery):
    alerts = []
    if battery < 15:
        alerts.append(f"🔋 Low Battery on {parcel.name}: {battery}%")
    if temp > 40:
        alerts.append(f"🔥 High Temperature on {parcel.name}: {temp}°C")
    if moist < parcel.moisture_threshold:
        alerts.append(f"💧 Critical Soil Moisture on {parcel.name}: {moist}% (Threshold: {parcel.moisture_threshold}%)")
    
    for alert in alerts:
        await send_alert(alert)

async def check_inactivity():
    while True:
        now = timezone.now()
        parcels = await get_active_parcels()
        for p in parcels:
            last_data = await get_last_sensor_data(p)
            if last_data and (now - last_data.timestamp > timedelta(hours=1)):
                await send_alert(f"⚠️ Inactivity Alert: No data from {p.name} for over 1 hour!")
        await asyncio.sleep(3600) # Check every hour

def on_connect(client, userdata, flags, reason_code, properties=None):
    print(f"Connected to MQTT broker with result code {reason_code}")
    client.subscribe(MQTT_TOPIC)

async def process_message(payload):
    device_id = payload.get("device_id")
    temp = payload.get("temperature")
    moist = payload.get("soil_moisture")
    battery = payload.get("battery_level", 100.0)
    rssi = payload.get("rssi", -50)
    humidity = payload.get("humidity", 50)

    if not device_id or temp is None or moist is None:
        return

    if not validate_data(temp, moist, battery):
        print(f"Discarded invalid data from {device_id}: Temp={temp}, Moist={moist}")
        return

    parcel = await save_telemetry_data(device_id, temp, moist, battery, rssi, humidity)
    await check_alerts(parcel, temp, moist, battery)
    print(f"[OK] Data saved to DB -> {device_id}: Temp={temp}°C, Moist={moist}%")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        # Run async processing safely
        asyncio.run(process_message(payload))
    except Exception as e:
        print(f"Error processing message: {e}")

def run_mqtt_worker():
    # Update to API Version 2 to fix DeprecationWarning
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
        print("MQTT Worker started. Listening for telemetry...")
        
        # Start inactivity checker in the main thread event loop
        asyncio.run(check_inactivity())
        
    except Exception as e:
        print(f"Failed to connect to MQTT broker: {e}")
        # Fallback loop if broker is missing just to keep inactivity checker alive
        asyncio.run(check_inactivity())

if __name__ == "__main__":
    run_mqtt_worker()
