"""
Django Entegrasyon - Views (Görünümler)
========================================

Bu dosya, veri analiz modülünün Django view'larını tanımlar.
REST API endpoint'leri ve template-based view'lar içerir.

Django ile Entegrasyon Mimarisi:
    1. URL → View → Analiz Servisi → Model → Template/JSON Response
    2. View'lar hem HTML template hem de JSON API response döner
    3. Plotly grafikleri HTML olarak template'e gömülür
"""

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.views.generic import ListView, DetailView
from django.utils import timezone
from django.db.models import Avg, Min, Max, Count
from django.core.paginator import Paginator
from datetime import timedelta
import pandas as pd
import json
import logging

from .models import Sensor, SensorVerisi, AnalizSonucu, SulamaOnerisi
from .analiz import (
    IstatistikselAnalizci,
    MakineOgrenmesiModeli,
    ZamanSerisiAnalizcisi,
    AnomaliTespitcisi,
)
from .gorsellestirme import GrafikOlusturucu

logger = logging.getLogger(__name__)


# =============================================================================
# TEMPLATE-BASED VIEWS
# =============================================================================

class DashboardView(View):
    """
    Ana dashboard sayfası.
    Tüm sensörlerin özet bilgilerini ve anlık durumlarını gösterir.
    """
    template_name = 'veri_analiz/dashboard.html'

    def get(self, request):
        # Aktif sensörler
        sensorler = Sensor.objects.filter(durum='aktif')

        # Son 24 saat verisi
        son_24_saat = timezone.now() - timedelta(hours=24)

        # Her sensör tipi için özet istatistikler
        ozet_istatistikler = {}
        for sensor in sensorler:
            son_veriler = SensorVerisi.objects.filter(
                sensor=sensor,
                olcum_zamani__gte=son_24_saat
            ).aggregate(
                ortalama=Avg('deger'),
                minimum=Min('deger'),
                maksimum=Max('deger'),
                veri_sayisi=Count('id'),
            )
            ozet_istatistikler[sensor.ad] = {
                'sensor': sensor,
                'istatistikler': son_veriler,
            }

        # Gauge grafikleri oluştur
        grafik = GrafikOlusturucu()
        gauge_grafikleri = {}
        for sensor in sensorler:
            son_veri = SensorVerisi.objects.filter(
                sensor=sensor
            ).order_by('-olcum_zamani').first()

            if son_veri:
                gauge_grafikleri[sensor.ad] = grafik.gauge_grafigi(
                    deger=son_veri.deger,
                    baslik=sensor.ad,
                    birim=son_veri.birim,
                )

        # Son sulama önerileri
        son_oneriler = SulamaOnerisi.objects.order_by('-olusturulma_zamani')[:5]

        context = {
            'sensorler': sensorler,
            'ozet_istatistikler': ozet_istatistikler,
            'gauge_grafikleri': gauge_grafikleri,
            'son_oneriler': son_oneriler,
            'toplam_sensor': sensorler.count(),
            'toplam_veri': SensorVerisi.objects.filter(
                olcum_zamani__gte=son_24_saat
            ).count(),
        }

        return render(request, self.template_name, context)


class SensorDetayView(DetailView):
    """
    Tekil sensör detay sayfası.
    Sensör verilerinin zaman serisi grafiği ve istatistikleri gösterilir.
    """
    model = Sensor
    template_name = 'veri_analiz/sensor_detay.html'
    context_object_name = 'sensor'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sensor = self.object

        # Son 7 günlük veriyi al
        son_7_gun = timezone.now() - timedelta(days=7)
        veriler = SensorVerisi.objects.filter(
            sensor=sensor,
            olcum_zamani__gte=son_7_gun
        ).order_by('olcum_zamani')

        if veriler.exists():
            # DataFrame'e dönüştür
            df = pd.DataFrame(list(veriler.values('deger', 'olcum_zamani')))

            # İstatistiksel analiz
            analizci = IstatistikselAnalizci(df)
            context['istatistikler'] = analizci.betimsel_istatistikler('deger')
            context['aykiri_degerler'] = analizci.aykiri_deger_tespiti('deger')

            # Grafik oluştur
            grafik = GrafikOlusturucu()
            context['zaman_serisi_html'] = grafik.interaktif_zaman_serisi(
                veri=df,
                deger_sutunu='deger',
                zaman_sutunu='olcum_zamani',
                baslik=f'{sensor.ad} - Son 7 Gün',
            )

            context['dagilim_grafigi'] = grafik.dagilim_grafigi(
                veri=df['deger'],
                baslik=f'{sensor.ad} - Veri Dağılımı',
            )

        return context


class AnalizSayfasiView(View):
    """
    Analiz sayfası - Kullanıcı analiz parametrelerini seçer ve sonuçları görür.
    """
    template_name = 'veri_analiz/analiz.html'

    def get(self, request):
        sensorler = Sensor.objects.filter(durum='aktif')
        son_analizler = AnalizSonucu.objects.order_by('-olusturulma_zamani')[:10]

        context = {
            'sensorler': sensorler,
            'son_analizler': son_analizler,
            'analiz_tipleri': AnalizSonucu.ANALIZ_TIPLERI,
        }
        return render(request, self.template_name, context)


class SensorListesiView(ListView):
    """Tüm sensörlerin listesi."""
    model = Sensor
    template_name = 'veri_analiz/sensor_listesi.html'
    context_object_name = 'sensorler'
    paginate_by = 20


# =============================================================================
# API VIEWS (JSON Responses)
# =============================================================================

class SensorVeriAPI(View):
    """
    Sensör verilerini JSON formatında döner.
    AJAX çağrıları ve frontend grafik güncellemeleri için kullanılır.
    """

    def get(self, request, sensor_id):
        sensor = get_object_or_404(Sensor, pk=sensor_id)

        # Query parametreleri
        gun_sayisi = int(request.GET.get('gun', 7))
        limit = int(request.GET.get('limit', 1000))

        baslangic = timezone.now() - timedelta(days=gun_sayisi)
        veriler = SensorVerisi.objects.filter(
            sensor=sensor,
            olcum_zamani__gte=baslangic
        ).order_by('olcum_zamani')[:limit]

        veri_listesi = [
            {
                'zaman': v.olcum_zamani.isoformat(),
                'deger': v.deger,
                'birim': v.birim,
                'kalite': v.kalite_skoru,
            }
            for v in veriler
        ]

        return JsonResponse({
            'sensor': {
                'id': sensor.id,
                'ad': sensor.ad,
                'tip': sensor.sensor_tipi,
                'bolge': sensor.bolge,
            },
            'veriler': veri_listesi,
            'toplam': len(veri_listesi),
        })


class IstatistikAPI(View):
    """
    Seçilen sensör için istatistiksel analiz API'si.
    """

    def get(self, request, sensor_id):
        sensor = get_object_or_404(Sensor, pk=sensor_id)
        gun_sayisi = int(request.GET.get('gun', 30))

        baslangic = timezone.now() - timedelta(days=gun_sayisi)
        veriler = SensorVerisi.objects.filter(
            sensor=sensor,
            olcum_zamani__gte=baslangic
        ).order_by('olcum_zamani')

        if not veriler.exists():
            return JsonResponse({'hata': 'Veri bulunamadı.'}, status=404)

        df = pd.DataFrame(list(veriler.values('deger', 'olcum_zamani')))
        analizci = IstatistikselAnalizci(df)

        istatistikler = analizci.betimsel_istatistikler('deger')
        aykiri = analizci.aykiri_deger_tespiti('deger')

        return JsonResponse({
            'sensor_id': sensor_id,
            'gun_sayisi': gun_sayisi,
            'istatistikler': istatistikler,
            'aykiri_degerler': {
                'toplam': aykiri['aykiri_deger_sayisi'],
                'oran': aykiri['aykiri_oran'],
            },
        })


class AnalizCalistirAPI(View):
    """
    Analiz çalıştırma API'si.
    POST ile analiz tipi ve parametreleri alıp sonuçları döner.
    """

    def post(self, request):
        try:
            veri = json.loads(request.body)
            sensor_id = veri.get('sensor_id')
            analiz_tipi = veri.get('analiz_tipi', 'istatistiksel')
            gun_sayisi = veri.get('gun_sayisi', 30)

            sensor = get_object_or_404(Sensor, pk=sensor_id)
            baslangic = timezone.now() - timedelta(days=gun_sayisi)
            bitis = timezone.now()

            veriler = SensorVerisi.objects.filter(
                sensor=sensor,
                olcum_zamani__gte=baslangic
            ).order_by('olcum_zamani')

            if not veriler.exists():
                return JsonResponse({'hata': 'Veri bulunamadı.'}, status=404)

            df = pd.DataFrame(list(veriler.values('deger', 'olcum_zamani')))

            # Analiz tipine göre analiz çalıştır
            sonuc = {}
            if analiz_tipi == 'istatistiksel':
                analizci = IstatistikselAnalizci(df)
                sonuc = analizci.betimsel_istatistikler('deger')
            elif analiz_tipi == 'anomali':
                tespitci = AnomaliTespitcisi(df)
                sonuc = tespitci.zscore_tespit('deger')
            elif analiz_tipi == 'zaman_serisi':
                zs = ZamanSerisiAnalizcisi(df.set_index('olcum_zamani')['deger'])
                sonuc = zs.duraganlik_testi()

            # Sonucu veritabanına kaydet
            analiz_kaydi = AnalizSonucu.objects.create(
                baslik=f"{sensor.ad} - {analiz_tipi.title()} Analizi",
                analiz_tipi=analiz_tipi,
                sensor=sensor,
                baslangic_tarihi=baslangic,
                bitis_tarihi=bitis,
                sonuc_verisi=sonuc,
            )

            return JsonResponse({
                'basarili': True,
                'analiz_id': analiz_kaydi.id,
                'sonuc': sonuc,
            })

        except Exception as e:
            logger.error(f"Analiz hatası: {e}")
            return JsonResponse({'hata': str(e)}, status=500)


class KorelasyonAPI(View):
    """
    Çoklu sensör korelasyon analizi API'si.
    """

    def get(self, request):
        sensor_idler = request.GET.getlist('sensor_id')
        gun_sayisi = int(request.GET.get('gun', 30))

        if len(sensor_idler) < 2:
            return JsonResponse(
                {'hata': 'En az 2 sensör seçilmelidir.'}, status=400
            )

        baslangic = timezone.now() - timedelta(days=gun_sayisi)
        pivot_data = {}

        for sid in sensor_idler:
            sensor = get_object_or_404(Sensor, pk=sid)
            veriler = SensorVerisi.objects.filter(
                sensor=sensor,
                olcum_zamani__gte=baslangic
            ).values_list('deger', flat=True)
            pivot_data[sensor.ad] = list(veriler)

        # Eşit uzunlukta olması için en kısa listeye göre kes
        min_len = min(len(v) for v in pivot_data.values())
        for key in pivot_data:
            pivot_data[key] = pivot_data[key][:min_len]

        df = pd.DataFrame(pivot_data)
        kor_matrisi = df.corr()

        # Isı haritası oluştur
        grafik = GrafikOlusturucu()
        isi_haritasi_html = grafik.korelasyon_isi_haritasi(kor_matrisi)

        return JsonResponse({
            'korelasyon_matrisi': kor_matrisi.to_dict(),
            'grafik_base64': isi_haritasi_html,
        })
