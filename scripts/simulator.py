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

from visualization.models import SensorData, SystemState, ActivityLog

def start_simulation():
    print("--- 🌿 Akıllı Tarım Profesyonel Simülasyonu Başlatıldı ---")
    
    last_data = SensorData.objects.order_by('-timestamp').first()
    current_soil_moisture = last_data.soil_moisture if last_data else 55.0

    while True:
        try:
            now = datetime.now()
            hour = now.hour + now.minute / 60
            
            # Sıcaklık döngüsü
            base_temp = 22.0
            amplitude = 8.0
            temp = base_temp + amplitude * math.sin((hour - 9) * math.pi / 12)
            temp += random.uniform(-0.15, 0.15) 

            state, _ = SystemState.objects.get_or_create(id=1)

            if state.is_irrigating:
                # Pump is active, moisture increases rapidly
                current_soil_moisture += 15.0
                if current_soil_moisture >= 85.0:
                    current_soil_moisture = 85.0
                    state.is_irrigating = False
                    state.save()
                    ActivityLog.objects.create(event_type="INFO", description="Irrigation Completed")
                    print("💧 Sulama tamamlandi.")
            else:
                # Buharlaşma mantığı (İlişkisel Veri)
                if temp > 25:
                    evaporation = random.uniform(0.04, 0.08)
                else:
                    evaporation = random.uniform(0.01, 0.03)
                
                current_soil_moisture -= evaporation

                # Otomatik Sulama Protokolü
                if current_soil_moisture < 25:
                    ActivityLog.objects.create(event_type="WARNING", description="Auto-irrigation triggered due to low moisture")
                    state.is_irrigating = True
                    state.save()
                    print("💧 Nem kritik! Otomatik sulama baslatiliyor...")

            SensorData.objects.create(
                temperature=round(temp, 2),
                humidity=random.uniform(45, 55),
                soil_moisture=round(current_soil_moisture, 2)
            )

            print(f"[{now.strftime('%H:%M:%S')}] Sicaklik: {temp:.2f}C | Nem: %{current_soil_moisture:.2f} | Pompa: {'ACIK' if state.is_irrigating else 'KAPALI'}")
            time.sleep(3)

        except KeyboardInterrupt:
            print("\nSimülasyon durduruldu.")
            break

if __name__ == "__main__":
    start_simulation()
