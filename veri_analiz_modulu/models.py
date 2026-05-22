"""
Veri Toplama ve Analiz Modülü - Veritabanı Modelleri

Bu dosya, IoT sensörlerinden toplanan tarımsal verilerin
veritabanı şemasını tanımlar. Django ORM kullanılarak
PostgreSQL/SQLite ile uyumlu çalışır.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Sensor(models.Model):
    """
    IoT sensör tanımları.
    Her sensör belirli bir tarla/bölge ile ilişkilendirilir.
    """
    SENSOR_TIPLERI = [
        ('toprak_nem', 'Toprak Nem Sensörü'),
        ('sicaklik', 'Sıcaklık Sensörü'),
        ('hava_nem', 'Hava Nem Sensörü'),
        ('isik', 'Işık Yoğunluğu Sensörü'),
        ('ph', 'Toprak pH Sensörü'),
        ('ruzgar', 'Rüzgar Hızı Sensörü'),
        ('yagis', 'Yağış Sensörü'),
        ('ec', 'Elektriksel İletkenlik (EC) Sensörü'),
    ]

    DURUM_SECENEKLERI = [
        ('aktif', 'Aktif'),
        ('pasif', 'Pasif'),
        ('bakim', 'Bakımda'),
        ('arizali', 'Arızalı'),
    ]

    ad = models.CharField(max_length=100, verbose_name="Sensör Adı")
    sensor_tipi = models.CharField(
        max_length=20,
        choices=SENSOR_TIPLERI,
        verbose_name="Sensör Tipi"
    )
    konum_enlem = models.FloatField(verbose_name="Enlem (Latitude)")
    konum_boylam = models.FloatField(verbose_name="Boylam (Longitude)")
    bolge = models.CharField(max_length=100, verbose_name="Bölge/Tarla Adı")
    durum = models.CharField(
        max_length=10,
        choices=DURUM_SECENEKLERI,
        default='aktif',
        verbose_name="Durum"
    )
    kurulum_tarihi = models.DateTimeField(
        default=timezone.now,
        verbose_name="Kurulum Tarihi"
    )
    son_kalibrasyon = models.DateTimeField(
        null=True, blank=True,
        verbose_name="Son Kalibrasyon Tarihi"
    )

    class Meta:
        verbose_name = "Sensör"
        verbose_name_plural = "Sensörler"
        ordering = ['-kurulum_tarihi']

    def __str__(self):
        return f"{self.ad} ({self.get_sensor_tipi_display()}) - {self.bolge}"


class SensorVerisi(models.Model):
    """
    Sensörlerden toplanan ham veriler.
    Her kayıt bir sensörün belirli bir zamandaki ölçüm değerini içerir.
    """
    sensor = models.ForeignKey(
        Sensor,
        on_delete=models.CASCADE,
        related_name='veriler',
        verbose_name="Sensör"
    )
    deger = models.FloatField(verbose_name="Ölçüm Değeri")
    birim = models.CharField(max_length=20, verbose_name="Birim")
    olcum_zamani = models.DateTimeField(
        default=timezone.now,
        verbose_name="Ölçüm Zamanı",
        db_index=True
    )
    kalite_skoru = models.FloatField(
        default=1.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="Veri Kalite Skoru"
    )
    islenmis = models.BooleanField(
        default=False,
        verbose_name="İşlenmiş mi?"
    )

    class Meta:
        verbose_name = "Sensör Verisi"
        verbose_name_plural = "Sensör Verileri"
        ordering = ['-olcum_zamani']
        indexes = [
            models.Index(fields=['sensor', 'olcum_zamani']),
            models.Index(fields=['olcum_zamani', 'islenmis']),
        ]

    def __str__(self):
        return f"{self.sensor.ad}: {self.deger} {self.birim} ({self.olcum_zamani})"


class AnalizSonucu(models.Model):
    """
    Veri analiz sonuçlarını saklayan model.
    İstatistiksel analiz ve ML tahminlerinin çıktıları burada tutulur.
    """
    ANALIZ_TIPLERI = [
        ('istatistiksel', 'İstatistiksel Analiz'),
        ('regresyon', 'Regresyon Analizi'),
        ('siniflandirma', 'Sınıflandırma'),
        ('kumeleme', 'Kümeleme Analizi'),
        ('zaman_serisi', 'Zaman Serisi Analizi'),
        ('anomali', 'Anomali Tespiti'),
        ('korelasyon', 'Korelasyon Analizi'),
    ]

    baslik = models.CharField(max_length=200, verbose_name="Analiz Başlığı")
    analiz_tipi = models.CharField(
        max_length=20,
        choices=ANALIZ_TIPLERI,
        verbose_name="Analiz Tipi"
    )
    sensor = models.ForeignKey(
        Sensor,
        on_delete=models.CASCADE,
        related_name='analizler',
        verbose_name="İlgili Sensör",
        null=True, blank=True
    )
    baslangic_tarihi = models.DateTimeField(verbose_name="Analiz Başlangıç Tarihi")
    bitis_tarihi = models.DateTimeField(verbose_name="Analiz Bitiş Tarihi")
    sonuc_verisi = models.JSONField(
        verbose_name="Sonuç Verisi (JSON)",
        help_text="Analiz sonuçlarını JSON formatında saklar"
    )
    dogruluk_orani = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        verbose_name="Doğruluk Oranı (%)"
    )
    model_parametreleri = models.JSONField(
        null=True, blank=True,
        verbose_name="Model Parametreleri"
    )
    olusturulma_zamani = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Oluşturulma Zamanı"
    )
    notlar = models.TextField(
        blank=True,
        verbose_name="Notlar/Açıklamalar"
    )

    class Meta:
        verbose_name = "Analiz Sonucu"
        verbose_name_plural = "Analiz Sonuçları"
        ordering = ['-olusturulma_zamani']

    def __str__(self):
        return f"{self.baslik} ({self.get_analiz_tipi_display()})"


class SulamaOnerisi(models.Model):
    """
    Analiz sonuçlarına göre oluşturulan sulama önerileri.
    ML modelleri tarafından otomatik üretilir.
    """
    ONCELIK_SEVIYELERI = [
        ('dusuk', 'Düşük'),
        ('orta', 'Orta'),
        ('yuksek', 'Yüksek'),
        ('acil', 'Acil'),
    ]

    bolge = models.CharField(max_length=100, verbose_name="Bölge")
    analiz = models.ForeignKey(
        AnalizSonucu,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='sulama_onerileri',
        verbose_name="İlgili Analiz"
    )
    oneri_metni = models.TextField(verbose_name="Öneri")
    oncelik = models.CharField(
        max_length=10,
        choices=ONCELIK_SEVIYELERI,
        default='orta',
        verbose_name="Öncelik"
    )
    onerilen_su_miktari = models.FloatField(
        null=True, blank=True,
        verbose_name="Önerilen Su Miktarı (litre/m²)"
    )
    onerilen_zaman = models.DateTimeField(
        null=True, blank=True,
        verbose_name="Önerilen Sulama Zamanı"
    )
    uygulandı = models.BooleanField(
        default=False,
        verbose_name="Uygulandı mı?"
    )
    olusturulma_zamani = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Oluşturulma Zamanı"
    )

    class Meta:
        verbose_name = "Sulama Önerisi"
        verbose_name_plural = "Sulama Önerileri"
        ordering = ['-olusturulma_zamani']

    def __str__(self):
        return f"{self.bolge} - {self.get_oncelik_display()} ({self.olusturulma_zamani})"
