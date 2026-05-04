import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from visualization.models import Parcel, ActivityLog

def reset_system():
    print("⚠️ DİKKAT: Veritabanı 'Hard Reset' işlemi başlatılıyor...")
    
    # İstenen tüm parsellerin is_irrigating ve is_active durumlarını False çek
    parcels = Parcel.objects.all()
    count = parcels.count()
    
    parcels.update(is_irrigating=False, is_active=False)
    
    # Log the reset
    ActivityLog.objects.create(
        event_type="SYSTEM_RESET",
        description=f"Admin tarafından sistem 'Hard Reset' edildi. {count} parsel deaktif konuma alındı."
    )
    
    print(f"✅ Başarılı! {count} parselin is_irrigating ve is_active durumu False yapıldı.")

if __name__ == "__main__":
    reset_system()
