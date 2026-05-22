"""
Django Admin Yapılandırması
============================

Sensör ve analiz verilerini Django admin panelinden yönetmek için
model kayıtları ve özelleştirmeler.
"""

from django.contrib import admin
from .models import Sensor, SensorVerisi, AnalizSonucu, SulamaOnerisi


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ('ad', 'sensor_tipi', 'bolge', 'durum', 'kurulum_tarihi')
    list_filter = ('sensor_tipi', 'durum', 'bolge')
    search_fields = ('ad', 'bolge')
    list_editable = ('durum',)
    readonly_fields = ('kurulum_tarihi',)


@admin.register(SensorVerisi)
class SensorVerisiAdmin(admin.ModelAdmin):
    list_display = ('sensor', 'deger', 'birim', 'olcum_zamani', 'kalite_skoru', 'islenmis')
    list_filter = ('sensor__sensor_tipi', 'islenmis', 'olcum_zamani')
    search_fields = ('sensor__ad',)
    date_hierarchy = 'olcum_zamani'
    list_per_page = 50


@admin.register(AnalizSonucu)
class AnalizSonucuAdmin(admin.ModelAdmin):
    list_display = ('baslik', 'analiz_tipi', 'sensor', 'dogruluk_orani', 'olusturulma_zamani')
    list_filter = ('analiz_tipi', 'olusturulma_zamani')
    search_fields = ('baslik', 'notlar')
    readonly_fields = ('olusturulma_zamani', 'sonuc_verisi', 'model_parametreleri')


@admin.register(SulamaOnerisi)
class SulamaOnerisiAdmin(admin.ModelAdmin):
    list_display = ('bolge', 'oncelik', 'onerilen_su_miktari', 'uygulandı', 'olusturulma_zamani')
    list_filter = ('oncelik', 'uygulandı', 'bolge')
    list_editable = ('uygulandı',)
