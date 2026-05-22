"""
Örnek Sensör Verisi Oluşturma Komutu
======================================

Django management command: Geliştirme/test ortamı için
gerçekçi simüle edilmiş sensör verileri oluşturur.

Kullanım:
    python manage.py ornek_veri_olustur --gun 30 --sensor-sayisi 5
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import numpy as np
import random

from veri_analiz_modulu.models import Sensor, SensorVerisi


class Command(BaseCommand):
    help = 'Geliştirme ortamı için örnek sensör verileri oluşturur'

    def add_arguments(self, parser):
        parser.add_argument(
            '--gun', type=int, default=30,
            help='Kaç günlük veri oluşturulacak (varsayılan: 30)'
        )
        parser.add_argument(
            '--sensor-sayisi', type=int, default=5,
            help='Oluşturulacak sensör sayısı (varsayılan: 5)'
        )

    def handle(self, *args, **options):
        gun = options['gun']
        sensor_sayisi = options['sensor_sayisi']

        self.stdout.write(self.style.SUCCESS(
            f'{sensor_sayisi} sensör ve {gun} günlük veri oluşturuluyor...'
        ))

        # Sensör tanımları
        sensor_tanimlari = [
            {
                'ad': 'Toprak Nem Sensörü - Tarla A',
                'sensor_tipi': 'toprak_nem',
                'bolge': 'Tarla A',
                'konum_enlem': 39.9208,
                'konum_boylam': 32.8541,
                'birim': '%',
                'ortalama': 55, 'std': 15, 'min': 10, 'max': 95,
            },
            {
                'ad': 'Sıcaklık Sensörü - Tarla A',
                'sensor_tipi': 'sicaklik',
                'bolge': 'Tarla A',
                'konum_enlem': 39.9210,
                'konum_boylam': 32.8543,
                'birim': '°C',
                'ortalama': 22, 'std': 8, 'min': -5, 'max': 45,
            },
            {
                'ad': 'Hava Nem Sensörü - Tarla A',
                'sensor_tipi': 'hava_nem',
                'bolge': 'Tarla A',
                'konum_enlem': 39.9212,
                'konum_boylam': 32.8545,
                'birim': '%',
                'ortalama': 60, 'std': 20, 'min': 15, 'max': 95,
            },
            {
                'ad': 'pH Sensörü - Tarla B',
                'sensor_tipi': 'ph',
                'bolge': 'Tarla B',
                'konum_enlem': 39.9300,
                'konum_boylam': 32.8600,
                'birim': 'pH',
                'ortalama': 6.8, 'std': 0.5, 'min': 4.0, 'max': 9.0,
            },
            {
                'ad': 'Rüzgar Hızı Sensörü - Tarla B',
                'sensor_tipi': 'ruzgar',
                'bolge': 'Tarla B',
                'konum_enlem': 39.9305,
                'konum_boylam': 32.8605,
                'birim': 'km/h',
                'ortalama': 12, 'std': 8, 'min': 0, 'max': 60,
            },
        ]

        toplam_veri = 0
        for i, tanim in enumerate(sensor_tanimlari[:sensor_sayisi]):
            # Sensör oluştur
            sensor, created = Sensor.objects.get_or_create(
                ad=tanim['ad'],
                defaults={
                    'sensor_tipi': tanim['sensor_tipi'],
                    'bolge': tanim['bolge'],
                    'konum_enlem': tanim['konum_enlem'],
                    'konum_boylam': tanim['konum_boylam'],
                    'durum': 'aktif',
                }
            )

            if created:
                self.stdout.write(f'  ✓ Sensör oluşturuldu: {sensor.ad}')

            # Veri noktaları oluştur (saatlik)
            baslangic = timezone.now() - timedelta(days=gun)
            veriler = []

            for saat in range(gun * 24):
                zaman = baslangic + timedelta(hours=saat)

                # Günlük döngü simülasyonu (sıcaklık vb.)
                gun_saati = zaman.hour
                gunluk_etki = np.sin((gun_saati - 6) * np.pi / 12) * tanim['std'] * 0.3

                # Rastgele değer + günlük döngü
                deger = np.random.normal(tanim['ortalama'] + gunluk_etki, tanim['std'] * 0.5)
                deger = np.clip(deger, tanim['min'], tanim['max'])

                # %2 olasılıkla anomali ekle
                if random.random() < 0.02:
                    deger = tanim['ortalama'] + np.random.choice([-1, 1]) * tanim['std'] * 3

                veriler.append(SensorVerisi(
                    sensor=sensor,
                    deger=round(deger, 2),
                    birim=tanim['birim'],
                    olcum_zamani=zaman,
                    kalite_skoru=round(random.uniform(0.85, 1.0), 2),
                ))

            # Toplu kaydetme (performans için)
            SensorVerisi.objects.bulk_create(veriler, ignore_conflicts=True)
            toplam_veri += len(veriler)
            self.stdout.write(f'  ✓ {len(veriler)} veri noktası oluşturuldu: {sensor.ad}')

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Toplam {toplam_veri} veri noktası başarıyla oluşturuldu!'
        ))
