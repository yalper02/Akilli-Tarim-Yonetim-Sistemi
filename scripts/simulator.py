import os
import django
import random
import time
import sys
import math
from datetime import datetime

# Django kurulumu
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from visualization.models import SensorData, SystemState, ActivityLog, Parcel

def start_simulation():
    print("--- Akilli Tarim Profesyonel Simulasyonu Baslatildi ---")
    
    # Ensure parcels exist
    parcels = []
    for i in range(1, 4):
        p, _ = Parcel.objects.get_or_create(name=f"Device_0{i}")
        parcels.append(p)

    while True:
        try:
            now = datetime.now()
            hour = now.hour + now.minute / 60
            
            # Sıcaklık döngüsü
            base_temp = 22.0
            amplitude = 8.0
            temp = base_temp + amplitude * math.sin((hour - 9) * math.pi / 12)
            temp += random.uniform(-0.15, 0.15) 

            for parcel in parcels:
                last_data = SensorData.objects.filter(parcel=parcel).order_by('-timestamp').first()
                current_soil_moisture = last_data.soil_moisture if last_data else random.uniform(40.0, 60.0)

                parcel.refresh_from_db()

                if parcel.is_irrigating:
                    current_soil_moisture += 15.0
                    if current_soil_moisture >= 85.0:
                        current_soil_moisture = 85.0
                        parcel.is_irrigating = False
                        parcel.save()
                        ActivityLog.objects.create(event_type="INFO", description=f"Irrigation Completed for {parcel.name}")
                        print(f"[Su] {parcel.name} sulama tamamlandi.")
                else:
                    if temp > 25:
                        evaporation = random.uniform(0.04, 0.08)
                    else:
                        evaporation = random.uniform(0.01, 0.03)
                    
                    current_soil_moisture -= evaporation

                    if current_soil_moisture < parcel.moisture_threshold:
                        ActivityLog.objects.create(event_type="WARNING", description=f"Auto-irrigation triggered for {parcel.name}")
                        parcel.is_irrigating = True
                        parcel.save()
                        print(f"[Su] {parcel.name} Nem kritik (< {parcel.moisture_threshold}%)! Otomatik sulama baslatiliyor...")

                parcel_temp = temp + random.uniform(-0.5, 0.5)

                SensorData.objects.create(
                    parcel=parcel,
                    device_name=parcel.name,
                    temperature=round(parcel_temp, 2),
                    humidity=random.uniform(45, 55),
                    soil_moisture=round(current_soil_moisture, 2)
                )

                print(f"[{now.strftime('%H:%M:%S')}] {parcel.name} | Sicaklik: {parcel_temp:.2f}C | Nem: %{current_soil_moisture:.2f} | Pompa: {'ACIK' if parcel.is_irrigating else 'KAPALI'}")
            
            time.sleep(3)

        except KeyboardInterrupt:
            print("\nSimülasyon durduruldu.")
            break

if __name__ == "__main__":
    start_simulation()
