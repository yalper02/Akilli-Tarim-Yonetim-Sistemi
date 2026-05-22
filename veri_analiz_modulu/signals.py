"""
Django Signals
===============

Sensör verisi kaydedildiğinde otomatik tetiklenen işlemler.
Örneğin: anomali tespiti, sulama önerisi oluşturma.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
import logging

from .models import SensorVerisi, SulamaOnerisi

logger = logging.getLogger(__name__)


@receiver(post_save, sender=SensorVerisi)
def veri_kaydedildi(sender, instance, created, **kwargs):
    """
    Yeni sensör verisi kaydedildiğinde tetiklenir.
    Kritik eşik değerleri aşıldığında uyarı oluşturur.
    """
    if not created:
        return

    # Toprak nemi kritik eşik kontrolü
    if instance.sensor.sensor_tipi == 'toprak_nem':
        if instance.deger < 20:
            SulamaOnerisi.objects.create(
                bolge=instance.sensor.bolge,
                oneri_metni=(
                    f"{instance.sensor.bolge} bölgesinde toprak nemi "
                    f"kritik seviyede düşük: {instance.deger}%. "
                    f"Acil sulama önerilir."
                ),
                oncelik='acil',
                onerilen_su_miktari=15.0,
            )
            logger.warning(
                f"KRİTİK: {instance.sensor.bolge} toprak nemi düşük: {instance.deger}%"
            )
        elif instance.deger < 35:
            SulamaOnerisi.objects.create(
                bolge=instance.sensor.bolge,
                oneri_metni=(
                    f"{instance.sensor.bolge} bölgesinde toprak nemi "
                    f"düşük seviyede: {instance.deger}%. "
                    f"Yakın zamanda sulama planlanmalı."
                ),
                oncelik='yuksek',
                onerilen_su_miktari=10.0,
            )

    # Sıcaklık don riski kontrolü
    elif instance.sensor.sensor_tipi == 'sicaklik':
        if instance.deger <= 0:
            logger.warning(
                f"DON RİSKİ: {instance.sensor.bolge} sıcaklık: {instance.deger}°C"
            )
