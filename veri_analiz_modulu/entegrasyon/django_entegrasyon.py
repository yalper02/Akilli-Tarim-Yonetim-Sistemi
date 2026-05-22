"""
Django Entegrasyon Kılavuzu
============================

Bu dosya, Veri Toplama ve Analiz Modülünün mevcut Django projesine
nasıl entegre edileceğini adım adım açıklar.

Aşağıdaki kodları ilgili Django dosyalarına eklemeniz gerekmektedir.
"""


# =============================================================================
# ADIM 1: settings.py - Uygulama Kaydı
# =============================================================================
"""
# proje/settings.py dosyasına ekleyin:

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Veri Toplama ve Analiz Modülü
    'veri_analiz_modulu',
]

# Loglama ayarları (opsiyonel ama önerilen)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'analiz.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'veri_analiz_modulu': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
"""


# =============================================================================
# ADIM 2: urls.py - URL Yapılandırması
# =============================================================================
"""
# proje/urls.py dosyasına ekleyin:

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Veri Analiz Modülü URL'leri
    path('analiz/', include('veri_analiz_modulu.urls')),
]
"""


# =============================================================================
# ADIM 3: Veritabanı Migration'ları
# =============================================================================
"""
Terminal komutları:

    # Migration dosyaları oluştur
    python manage.py makemigrations veri_analiz_modulu
    
    # Migration'ları uygula (tabloları oluştur)
    python manage.py migrate
    
    # Örnek veri oluştur (geliştirme ortamı için)
    python manage.py ornek_veri_olustur --gun 30 --sensor-sayisi 5
"""


# =============================================================================
# ADIM 4: Bağımlılıkların Kurulumu
# =============================================================================
"""
Terminal komutu:

    pip install -r veri_analiz_modulu/requirements.txt
"""


# =============================================================================
# ADIM 5: Kullanım Örnekleri
# =============================================================================

def ornek_istatistiksel_analiz():
    """İstatistiksel analiz kullanım örneği."""
    import pandas as pd
    from veri_analiz_modulu.analiz import IstatistikselAnalizci

    # Sensör verilerini al (Django ORM)
    from veri_analiz_modulu.models import SensorVerisi
    
    veriler = SensorVerisi.objects.filter(
        sensor__sensor_tipi='toprak_nem'
    ).values('deger', 'olcum_zamani')
    
    df = pd.DataFrame(list(veriler))
    
    # Analiz yap
    analizci = IstatistikselAnalizci(df)
    istatistikler = analizci.betimsel_istatistikler('deger')
    print("İstatistikler:", istatistikler)
    
    # Korelasyon analizi (iki sensör arasında)
    korelasyon = analizci.korelasyon_analizi('toprak_nem', 'sicaklik')
    print("Korelasyon:", korelasyon)


def ornek_makine_ogrenmesi():
    """Makine öğrenmesi kullanım örneği."""
    import pandas as pd
    from veri_analiz_modulu.analiz import MakineOgrenmesiModeli

    # Örnek veri hazırla
    from veri_analiz_modulu.models import SensorVerisi
    
    veriler = SensorVerisi.objects.all().values(
        'sensor__sensor_tipi', 'deger', 'olcum_zamani'
    )
    df = pd.DataFrame(list(veriler))
    
    # Pivot tablo oluştur (her sensör tipi bir sütun olsun)
    pivot = df.pivot_table(
        index='olcum_zamani', 
        columns='sensor__sensor_tipi', 
        values='deger', 
        aggfunc='mean'
    ).dropna()
    
    # Model eğit
    model = MakineOgrenmesiModeli()
    X = pivot.drop(columns=['toprak_nem'])  # Bağımsız değişkenler
    y = pivot['toprak_nem']                  # Bağımlı değişken
    
    model.veri_hazirla(X, y)
    sonuc = model.model_egit(
        model_adi='random_forest',
        gorev='regresyon'
    )
    print("Model sonuçları:", sonuc)
    print("Özellik önemleri:", model.ozellik_onemi())


def ornek_zaman_serisi():
    """Zaman serisi analizi kullanım örneği."""
    import pandas as pd
    from veri_analiz_modulu.analiz import ZamanSerisiAnalizcisi

    from veri_analiz_modulu.models import SensorVerisi
    
    veriler = SensorVerisi.objects.filter(
        sensor__sensor_tipi='sicaklik'
    ).order_by('olcum_zamani').values('deger', 'olcum_zamani')
    
    df = pd.DataFrame(list(veriler))
    seri = df.set_index('olcum_zamani')['deger']
    
    # Zaman serisi analizi
    analizci = ZamanSerisiAnalizcisi(seri, frekans='H')
    
    # Durağanlık testi
    print("Durağanlık:", analizci.duraganlik_testi())
    
    # ARIMA tahmin
    tahmin = analizci.arima_tahmin(tahmin_adim=48)  # 48 saat ileri
    print("Tahminler:", tahmin['tahminler'][:5])


def ornek_gorsellestirme():
    """Görselleştirme kullanım örneği."""
    import pandas as pd
    from veri_analiz_modulu.gorsellestirme import GrafikOlusturucu

    from veri_analiz_modulu.models import SensorVerisi
    
    veriler = SensorVerisi.objects.filter(
        sensor__sensor_tipi='toprak_nem'
    ).order_by('olcum_zamani').values('deger', 'olcum_zamani')
    
    df = pd.DataFrame(list(veriler))
    
    grafik = GrafikOlusturucu(kayit_dizini='media/grafikler/')
    
    # İnteraktif zaman serisi
    html = grafik.interaktif_zaman_serisi(
        veri=df,
        deger_sutunu='deger',
        zaman_sutunu='olcum_zamani',
        baslik='Toprak Nemi Değişimi'
    )
    
    # Bu HTML'i Django template'e gönderin:
    # return render(request, 'sayfa.html', {'grafik_html': html})


# =============================================================================
# ADIM 6: Proje Yapısı Özeti
# =============================================================================
"""
Entegrasyon sonrası proje yapısı:

proje/
├── manage.py
├── proje/
│   ├── settings.py          ← INSTALLED_APPS'e 'veri_analiz_modulu' ekle
│   ├── urls.py               ← include('veri_analiz_modulu.urls') ekle
│   └── wsgi.py
│
├── veri_analiz_modulu/        ← Bu modül
│   ├── __init__.py
│   ├── apps.py                # Django app konfigürasyonu
│   ├── models.py              # Veritabanı modelleri (Sensor, SensorVerisi, vb.)
│   ├── views.py               # View'lar (Dashboard, API endpoint'leri)
│   ├── urls.py                # URL desenleri
│   ├── admin.py               # Admin paneli kayıtları
│   ├── signals.py             # Otomatik uyarı sistemi
│   │
│   ├── analiz/                # Analiz algoritmaları
│   │   ├── istatistiksel_analiz.py   # Betimsel istatistik, korelasyon, regresyon
│   │   ├── makine_ogrenmesi.py       # Random Forest, SVM, KNN, kümeleme
│   │   ├── zaman_serisi_analiz.py    # ARIMA, Holt-Winters, mevsimsel analiz
│   │   └── anomali_tespiti.py        # Isolation Forest, LOF, Z-Score
│   │
│   ├── gorsellestirme/       # Görselleştirme modülü
│   │   └── grafik_olusturucu.py      # Matplotlib, Seaborn, Plotly grafikleri
│   │
│   ├── entegrasyon/          # Entegrasyon kılavuzu
│   │   └── django_entegrasyon.py     # Bu dosya
│   │
│   ├── templates/            # Django HTML şablonları
│   │   └── veri_analiz/
│   │       └── dashboard.html        # Ana dashboard sayfası
│   │
│   ├── management/commands/  # Django yönetim komutları
│   │   └── ornek_veri_olustur.py     # Test verisi üreteci
│   │
│   └── requirements.txt      # Python bağımlılıkları
│
└── requirements.txt           # Ana proje bağımlılıkları
"""
