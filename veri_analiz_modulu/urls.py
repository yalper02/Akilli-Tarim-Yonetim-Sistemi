"""
Django URL Yapılandırması
=========================

Veri Toplama ve Analiz Modülü URL desenleri.
Ana urls.py dosyasına şu şekilde dahil edilir:

    # proje/urls.py
    from django.urls import path, include
    
    urlpatterns = [
        path('analiz/', include('veri_analiz_modulu.urls')),
    ]
"""

from django.urls import path
from . import views

app_name = 'veri_analiz'

urlpatterns = [
    # =========================================================================
    # SAYFA GÖRÜNÜMLERI (Template-based)
    # =========================================================================
    path(
        '',
        views.DashboardView.as_view(),
        name='dashboard'
    ),
    path(
        'sensorler/',
        views.SensorListesiView.as_view(),
        name='sensor_listesi'
    ),
    path(
        'sensor/<int:pk>/',
        views.SensorDetayView.as_view(),
        name='sensor_detay'
    ),
    path(
        'analiz/',
        views.AnalizSayfasiView.as_view(),
        name='analiz_sayfasi'
    ),

    # =========================================================================
    # API ENDPOINT'LERİ (JSON Responses)
    # =========================================================================
    path(
        'api/sensor/<int:sensor_id>/veri/',
        views.SensorVeriAPI.as_view(),
        name='api_sensor_veri'
    ),
    path(
        'api/sensor/<int:sensor_id>/istatistik/',
        views.IstatistikAPI.as_view(),
        name='api_istatistik'
    ),
    path(
        'api/analiz/',
        views.AnalizCalistirAPI.as_view(),
        name='api_analiz_calistir'
    ),
    path(
        'api/korelasyon/',
        views.KorelasyonAPI.as_view(),
        name='api_korelasyon'
    ),
]
