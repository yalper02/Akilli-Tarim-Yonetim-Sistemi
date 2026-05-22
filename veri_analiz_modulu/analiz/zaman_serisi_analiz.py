"""
Zaman Serisi Analiz Modülü
============================

Bu modül, sensör verilerinin zamana bağlı analizini gerçekleştirir.
Tarımsal verilerde mevsimsellik, trend ve döngüsel örüntüleri tespit eder.

Kullanılan Algoritmalar:
    - ARIMA (AutoRegressive Integrated Moving Average)
    - Mevsimsel Ayrıştırma (Seasonal Decomposition)
    - Holt-Winters Üstel Düzeltme
    - Prophet benzeri trend analizi
    
Kütüphaneler:
    - statsmodels: Zaman serisi modelleri
    - pandas: Veri manipülasyonu
    - numpy: Sayısal hesaplamalar
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
import logging
import warnings

from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.stattools import adfuller, acf, pacf
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error, mean_absolute_error

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)


class ZamanSerisiAnalizcisi:
    """
    Tarımsal sensör verileri için zaman serisi analiz sınıfı.
    
    Bu sınıf, sensör verilerindeki zamansal örüntüleri tespit eder
    ve gelecek değerleri tahmin eder.
    
    Kullanım Örneği:
        >>> analizci = ZamanSerisiAnalizcisi(veri_serisi, frekans='D')
        >>> ayristirma = analizci.mevsimsel_ayristirma()
        >>> tahmin = analizci.arima_tahmin(tahmin_adim=30)
    """

    def __init__(self, veri: pd.Series, frekans: str = 'D'):
        """
        Args:
            veri: Zaman indeksli pandas Series
            frekans: Veri frekansı ('H': saatlik, 'D': günlük, 'W': haftalık)
        """
        self.veri = veri.copy()
        self.frekans = frekans
        self._veri_hazirla()

    def _veri_hazirla(self):
        """Zaman serisi verisini hazırlar."""
        # İndeksin DatetimeIndex olduğundan emin ol
        if not isinstance(self.veri.index, pd.DatetimeIndex):
            self.veri.index = pd.to_datetime(self.veri.index)

        # Frekans ata
        self.veri = self.veri.asfreq(self.frekans)

        # Eksik değerleri interpolasyon ile doldur
        self.veri = self.veri.interpolate(method='time')

        logger.info(f"Zaman serisi hazırlandı: {len(self.veri)} veri noktası")

    # =========================================================================
    # 1. DURAĞANLIK TESTİ
    # =========================================================================

    def duraganlik_testi(self) -> Dict[str, Any]:
        """
        Augmented Dickey-Fuller (ADF) testi ile serinin durağanlığını test eder.
        
        Durağanlık, zaman serisi modellemesinde kritik bir ön koşuldur.
        Durağan olmayan serilerde fark alma (differencing) uygulanır.
        
        Returns:
            ADF test istatistiği, p-değeri ve durağanlık kararı
        """
        adf_sonuc = adfuller(self.veri.dropna())

        sonuc = {
            'adf_istatistik': float(adf_sonuc[0]),
            'p_degeri': float(adf_sonuc[1]),
            'kullanilan_gecikme': int(adf_sonuc[2]),
            'gozlem_sayisi': int(adf_sonuc[3]),
            'kritik_degerler': {
                k: float(v) for k, v in adf_sonuc[4].items()
            },
            'duragan_mi': adf_sonuc[1] < 0.05,
            'yorum': (
                "Seri durağandır (H0 reddedildi). Doğrudan modelleme yapılabilir."
                if adf_sonuc[1] < 0.05
                else "Seri durağan değildir. Fark alma işlemi gerekebilir."
            ),
        }

        logger.info(f"Durağanlık testi: {'Durağan' if sonuc['duragan_mi'] else 'Durağan Değil'}")
        return sonuc

    # =========================================================================
    # 2. MEVSİMSEL AYRIŞTIRMA
    # =========================================================================

    def mevsimsel_ayristirma(
        self, periyot: Optional[int] = None, model: str = 'additive'
    ) -> Dict[str, Any]:
        """
        Zaman serisini Trend, Mevsimsellik ve Artık bileşenlerine ayırır.
        
        Tarımsal verilerde mevsimsellik çok önemlidir:
            - Sıcaklık: Yıllık mevsimsellik (yaz/kış döngüsü)
            - Toprak nemi: Haftalık/günlük sulama döngüsü
            - Işık: Günlük güneş döngüsü
        
        Args:
            periyot: Mevsimsel periyot (None ise otomatik tespit)
            model: Ayrıştırma modeli ('additive' veya 'multiplicative')
            
        Returns:
            Trend, mevsimsel ve artık bileşenleri
        """
        if periyot is None:
            frekans_periyot = {
                'H': 24,      # Saatlik → günlük döngü
                'D': 7,       # Günlük → haftalık döngü
                'W': 52,      # Haftalık → yıllık döngü
                'M': 12,      # Aylık → yıllık döngü
            }
            periyot = frekans_periyot.get(self.frekans, 7)

        ayristirma = seasonal_decompose(
            self.veri.dropna(),
            model=model,
            period=periyot
        )

        sonuc = {
            'model_tipi': model,
            'periyot': periyot,
            'trend': ayristirma.trend.dropna().tolist(),
            'mevsimsel': ayristirma.seasonal.dropna().tolist(),
            'artik': ayristirma.resid.dropna().tolist(),
            'trend_istatistik': {
                'ortalama': float(ayristirma.trend.dropna().mean()),
                'std': float(ayristirma.trend.dropna().std()),
            },
            'mevsimsel_guc': float(ayristirma.seasonal.dropna().std()),
            'artik_istatistik': {
                'ortalama': float(ayristirma.resid.dropna().mean()),
                'std': float(ayristirma.resid.dropna().std()),
            },
        }

        # Bileşenleri sakla (görselleştirme için)
        self._ayristirma = ayristirma

        logger.info(f"Mevsimsel ayrıştırma tamamlandı (model: {model}, periyot: {periyot})")
        return sonuc

    # =========================================================================
    # 3. ARIMA MODELİ
    # =========================================================================

    def arima_tahmin(
        self,
        order: Tuple[int, int, int] = (1, 1, 1),
        tahmin_adim: int = 30,
        otomatik_order: bool = True
    ) -> Dict[str, Any]:
        """
        ARIMA modeli ile gelecek tahminleri yapar.
        
        ARIMA Bileşenleri:
            - AR (p): Otoregresif bileşen - geçmiş değerlerin etkisi
            - I (d): Entegrasyon derecesi - kaç kez fark alındığı
            - MA (q): Hareketli ortalama - geçmiş hataların etkisi
        
        Tarımsal uygulamada ARIMA:
            - Gelecek haftanın toprak nem değerlerini tahmin etme
            - Sıcaklık trendini öngörme
            - Sulama planlaması için verileri modellem
        
        Args:
            order: ARIMA (p, d, q) parametreleri
            tahmin_adim: Kaç adım ileriye tahmin yapılacak
            otomatik_order: Otomatik parametre seçimi
            
        Returns:
            Tahmin değerleri, güven aralıkları ve model metrikleri
        """
        veri_temiz = self.veri.dropna()

        if otomatik_order:
            order = self._optimal_arima_order(veri_temiz)

        try:
            model = ARIMA(veri_temiz, order=order)
            model_fit = model.fit()

            # Tahmin yap
            tahmin = model_fit.forecast(steps=tahmin_adim)
            guven_araligi = model_fit.get_forecast(steps=tahmin_adim)
            guven_df = guven_araligi.conf_int()

            # Model performansı (in-sample)
            y_tahmin = model_fit.predict(start=0, end=len(veri_temiz) - 1)
            rmse = np.sqrt(mean_squared_error(
                veri_temiz.iloc[order[1]:], y_tahmin.iloc[order[1]:]
            ))

            sonuc = {
                'order': order,
                'tahminler': tahmin.tolist(),
                'tahmin_tarihleri': tahmin.index.strftime('%Y-%m-%d').tolist(),
                'guven_araligi_alt': guven_df.iloc[:, 0].tolist(),
                'guven_araligi_ust': guven_df.iloc[:, 1].tolist(),
                'rmse': float(rmse),
                'aic': float(model_fit.aic),
                'bic': float(model_fit.bic),
                'model_ozeti': str(model_fit.summary()),
            }

            logger.info(f"ARIMA{order} tahmin tamamlandı: {tahmin_adim} adım")
            return sonuc

        except Exception as e:
            logger.error(f"ARIMA modeli hatası: {e}")
            return {'hata': str(e), 'order': order}

    def _optimal_arima_order(
        self, veri: pd.Series, max_order: int = 3
    ) -> Tuple[int, int, int]:
        """
        AIC kriterine göre optimal ARIMA parametrelerini bulur.
        
        Args:
            veri: Zaman serisi verisi
            max_order: Maksimum p, d, q değeri
            
        Returns:
            Optimal (p, d, q) parametreleri
        """
        en_iyi_aic = float('inf')
        en_iyi_order = (1, 1, 1)

        # Durağanlık kontrolü ile d değerini belirle
        d = 0
        veri_test = veri.copy()
        while d < max_order:
            adf_p = adfuller(veri_test.dropna())[1]
            if adf_p < 0.05:
                break
            veri_test = veri_test.diff().dropna()
            d += 1

        # p ve q değerlerini ara
        for p in range(max_order + 1):
            for q in range(max_order + 1):
                try:
                    model = ARIMA(veri, order=(p, d, q))
                    model_fit = model.fit()
                    if model_fit.aic < en_iyi_aic:
                        en_iyi_aic = model_fit.aic
                        en_iyi_order = (p, d, q)
                except Exception:
                    continue

        logger.info(f"Optimal ARIMA order: {en_iyi_order} (AIC: {en_iyi_aic:.2f})")
        return en_iyi_order

    # =========================================================================
    # 4. HOLT-WINTERS ÜSTEL DÜZELTME
    # =========================================================================

    def holt_winters_tahmin(
        self,
        tahmin_adim: int = 30,
        mevsimsel_periyot: int = 7,
        trend: str = 'add',
        mevsimsel: str = 'add'
    ) -> Dict[str, Any]:
        """
        Holt-Winters Üstel Düzeltme ile tahmin yapar.
        
        Bu yöntem trend ve mevsimselliği aynı anda modelleyebilir.
        Tarımsal verilerde özellikle kısa vadeli tahminlerde etkilidir.
        
        Args:
            tahmin_adim: Tahmin adım sayısı
            mevsimsel_periyot: Mevsimsel periyot
            trend: Trend bileşeni ('add', 'mul', None)
            mevsimsel: Mevsimsel bileşen ('add', 'mul', None)
            
        Returns:
            Tahmin değerleri ve model bilgileri
        """
        veri_temiz = self.veri.dropna()

        try:
            model = ExponentialSmoothing(
                veri_temiz,
                trend=trend,
                seasonal=mevsimsel,
                seasonal_periods=mevsimsel_periyot
            )
            model_fit = model.fit(optimized=True)

            # Tahmin
            tahmin = model_fit.forecast(steps=tahmin_adim)

            # Model metrikleri
            y_tahmin_insample = model_fit.fittedvalues
            rmse = np.sqrt(mean_squared_error(veri_temiz, y_tahmin_insample))

            sonuc = {
                'tahminler': tahmin.tolist(),
                'tahmin_tarihleri': tahmin.index.strftime('%Y-%m-%d').tolist(),
                'rmse': float(rmse),
                'mae': float(mean_absolute_error(veri_temiz, y_tahmin_insample)),
                'duzeltme_parametreleri': {
                    'alpha': float(model_fit.params.get('smoothing_level', 0)),
                    'beta': float(model_fit.params.get('smoothing_trend', 0)),
                    'gamma': float(model_fit.params.get('smoothing_seasonal', 0)),
                },
                'aic': float(model_fit.aic),
            }

            logger.info(f"Holt-Winters tahmin tamamlandı: {tahmin_adim} adım")
            return sonuc

        except Exception as e:
            logger.error(f"Holt-Winters hatası: {e}")
            return {'hata': str(e)}

    # =========================================================================
    # 5. OTOKORELASİYON ANALİZİ
    # =========================================================================

    def otokorelasyon_analizi(self, max_gecikme: int = 40) -> Dict[str, Any]:
        """
        ACF ve PACF analizi - ARIMA parametre seçimi için kullanılır.
        
        ACF (Otokorelasyon): Serinin geçmiş değerleriyle korelasyonu
        PACF (Kısmi Otokorelasyon): Diğer gecikmelerin etkisi arındırılmış korelasyon
        
        Args:
            max_gecikme: Maksimum gecikme sayısı
            
        Returns:
            ACF ve PACF değerleri
        """
        veri_temiz = self.veri.dropna()

        acf_degerler = acf(veri_temiz, nlags=max_gecikme)
        pacf_degerler = pacf(veri_temiz, nlags=max_gecikme)

        # Güven aralığı (yaklaşık %95)
        guven_siniri = 1.96 / np.sqrt(len(veri_temiz))

        return {
            'acf': acf_degerler.tolist(),
            'pacf': pacf_degerler.tolist(),
            'guven_siniri': float(guven_siniri),
            'max_gecikme': max_gecikme,
            'anlamli_gecikme_sayisi_acf': int(
                np.sum(np.abs(acf_degerler[1:]) > guven_siniri)
            ),
            'anlamli_gecikme_sayisi_pacf': int(
                np.sum(np.abs(pacf_degerler[1:]) > guven_siniri)
            ),
        }
