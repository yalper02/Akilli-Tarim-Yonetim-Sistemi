"""
Anomali Tespit Modülü
======================

Bu modül, IoT sensör verilerindeki anormal değerleri tespit eder.
Sensör arızaları, olağandışı hava koşulları veya sulama problemleri
gibi anomalileri otomatik olarak belirler.

Kullanılan Algoritmalar:
    - Z-Score Yöntemi
    - Isolation Forest
    - IQR (Çeyrekler Arası Aralık) Yöntemi
    - Hareketli Ortalama Bazlı Tespit
    - Local Outlier Factor (LOF)

Kütüphaneler:
    - scikit-learn: Isolation Forest, LOF
    - scipy: Z-Score
    - numpy/pandas: Veri işleme
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any
from scipy import stats
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
import logging

logger = logging.getLogger(__name__)


class AnomaliTespitcisi:
    """
    IoT sensör verilerinde anomali tespiti yapan sınıf.
    
    Tarımsal uygulamada anomali örnekleri:
        - Sensör arızası: Aniden 0 veya çok yüksek değer okuması
        - Boru patlaması: Ani toprak nemi artışı
        - Don olayı: Beklenmeyen sıcaklık düşüşü
        - Zararlı istilası: Anormal bitki sağlığı metrikleri
    
    Kullanım Örneği:
        >>> tespitci = AnomaliTespitcisi(sensor_verisi)
        >>> anomaliler = tespitci.isolation_forest_tespit()
        >>> rapor = tespitci.anomali_raporu()
    """

    def __init__(self, veri: pd.DataFrame):
        """
        Args:
            veri: Sensör verilerini içeren DataFrame
        """
        self.veri = veri.copy()
        self.anomali_sonuclari: Dict[str, Any] = {}

    # =========================================================================
    # 1. Z-SCORE YÖNTEMİ
    # =========================================================================

    def zscore_tespit(
        self, sutun: str, esik: float = 3.0
    ) -> Dict[str, Any]:
        """
        Z-Score yöntemi ile anomali tespiti.
        
        Z-Score, bir değerin ortalamadan kaç standart sapma uzakta
        olduğunu ölçer. |Z| > eşik olan değerler anomali olarak işaretlenir.
        
        Args:
            sutun: Analiz edilecek sütun
            esik: Z-score eşik değeri (varsayılan: 3.0)
            
        Returns:
            Anomali tespiti sonuçları
        """
        veri_serisi = self.veri[sutun].dropna()
        z_skorlar = np.abs(stats.zscore(veri_serisi))

        anomali_maske = z_skorlar > esik
        anomali_indeksler = veri_serisi.index[anomali_maske].tolist()
        anomali_degerler = veri_serisi[anomali_maske].tolist()

        sonuc = {
            'yontem': 'Z-Score',
            'esik': esik,
            'toplam_veri': len(veri_serisi),
            'anomali_sayisi': int(anomali_maske.sum()),
            'anomali_orani': float(anomali_maske.sum() / len(veri_serisi) * 100),
            'anomali_indeksler': anomali_indeksler,
            'anomali_degerler': anomali_degerler,
            'ortalama': float(veri_serisi.mean()),
            'std': float(veri_serisi.std()),
        }

        self.anomali_sonuclari['zscore'] = sonuc
        return sonuc

    # =========================================================================
    # 2. ISOLATION FOREST
    # =========================================================================

    def isolation_forest_tespit(
        self,
        sutunlar: Optional[List[str]] = None,
        kontaminasyon: float = 0.05,
        n_estimators: int = 100
    ) -> Dict[str, Any]:
        """
        Isolation Forest ile anomali tespiti.
        
        Isolation Forest, veri noktalarını izole etmek için gereken
        ortalama bölme sayısını kullanır. Anomaliler daha az bölme
        ile izole edilebilir.
        
        Avantajları:
            - Çok boyutlu verilerde etkili
            - Büyük veri setlerinde hızlı
            - Parametreye az bağımlı
        
        Args:
            sutunlar: Analiz edilecek sütunlar (None ise tüm sayısal sütunlar)
            kontaminasyon: Beklenen anomali oranı (0-0.5 arası)
            n_estimators: Ağaç sayısı
            
        Returns:
            Anomali tespiti sonuçları
        """
        if sutunlar is None:
            sutunlar = self.veri.select_dtypes(include=[np.number]).columns.tolist()

        X = self.veri[sutunlar].dropna()

        model = IsolationForest(
            n_estimators=n_estimators,
            contamination=kontaminasyon,
            random_state=42,
            n_jobs=-1
        )

        tahminler = model.fit_predict(X)
        anomali_skorlari = model.decision_function(X)

        # -1: anomali, 1: normal
        anomali_maske = tahminler == -1

        sonuc = {
            'yontem': 'Isolation Forest',
            'kontaminasyon': kontaminasyon,
            'n_estimators': n_estimators,
            'toplam_veri': len(X),
            'anomali_sayisi': int(anomali_maske.sum()),
            'anomali_orani': float(anomali_maske.sum() / len(X) * 100),
            'anomali_indeksler': X.index[anomali_maske].tolist(),
            'anomali_skorlari': anomali_skorlari[anomali_maske].tolist(),
            'skor_esik': float(model.offset_),
            'kullanilan_ozellikler': sutunlar,
        }

        self.anomali_sonuclari['isolation_forest'] = sonuc
        return sonuc

    # =========================================================================
    # 3. LOCAL OUTLIER FACTOR (LOF)
    # =========================================================================

    def lof_tespit(
        self,
        sutunlar: Optional[List[str]] = None,
        n_neighbors: int = 20,
        kontaminasyon: float = 0.05
    ) -> Dict[str, Any]:
        """
        Local Outlier Factor (LOF) ile anomali tespiti.
        
        LOF, her veri noktasının yerel yoğunluğunu komşularıyla
        karşılaştırarak anomalileri tespit eder. Yoğunluğu düşük
        bölgelerdeki noktalar anomali olarak işaretlenir.
        
        Args:
            sutunlar: Analiz edilecek sütunlar
            n_neighbors: Komşu sayısı
            kontaminasyon: Beklenen anomali oranı
            
        Returns:
            LOF anomali tespiti sonuçları
        """
        if sutunlar is None:
            sutunlar = self.veri.select_dtypes(include=[np.number]).columns.tolist()

        X = self.veri[sutunlar].dropna()

        model = LocalOutlierFactor(
            n_neighbors=n_neighbors,
            contamination=kontaminasyon,
            n_jobs=-1
        )

        tahminler = model.fit_predict(X)
        negatif_lof_skorlari = model.negative_outlier_factor_

        anomali_maske = tahminler == -1

        sonuc = {
            'yontem': 'Local Outlier Factor',
            'n_neighbors': n_neighbors,
            'kontaminasyon': kontaminasyon,
            'toplam_veri': len(X),
            'anomali_sayisi': int(anomali_maske.sum()),
            'anomali_orani': float(anomali_maske.sum() / len(X) * 100),
            'anomali_indeksler': X.index[anomali_maske].tolist(),
            'lof_skorlari': negatif_lof_skorlari[anomali_maske].tolist(),
        }

        self.anomali_sonuclari['lof'] = sonuc
        return sonuc

    # =========================================================================
    # 4. HAREKETLİ ORTALAMA BAZLI TESPİT
    # =========================================================================

    def hareketli_ortalama_tespit(
        self,
        sutun: str,
        pencere: int = 24,
        esik_carpani: float = 2.0
    ) -> Dict[str, Any]:
        """
        Hareketli ortalama bazlı anomali tespiti.
        
        Mevcut değer ile hareketli ortalama arasındaki fark,
        hareketli standart sapmanın belirli bir katından büyükse
        anomali olarak işaretlenir.
        
        IoT sensör verilerinde sıklıkla kullanılır çünkü:
            - Gerçek zamanlı uygulanabilir
            - Mevsimsel değişikliklere uyum sağlar
            - Düşük hesaplama maliyeti
        
        Args:
            sutun: Analiz edilecek sütun
            pencere: Hareketli ortalama pencere boyutu
            esik_carpani: Standart sapma çarpanı
            
        Returns:
            Hareketli ortalama bazlı anomali sonuçları
        """
        veri_serisi = self.veri[sutun].dropna()

        hareketli_ort = veri_serisi.rolling(window=pencere, center=False).mean()
        hareketli_std = veri_serisi.rolling(window=pencere, center=False).std()

        ust_sinir = hareketli_ort + esik_carpani * hareketli_std
        alt_sinir = hareketli_ort - esik_carpani * hareketli_std

        anomali_maske = (veri_serisi > ust_sinir) | (veri_serisi < alt_sinir)
        # NaN değerlerini False yap
        anomali_maske = anomali_maske.fillna(False)

        sonuc = {
            'yontem': 'Hareketli Ortalama',
            'pencere_boyutu': pencere,
            'esik_carpani': esik_carpani,
            'toplam_veri': len(veri_serisi),
            'anomali_sayisi': int(anomali_maske.sum()),
            'anomali_orani': float(anomali_maske.sum() / len(veri_serisi) * 100),
            'anomali_indeksler': veri_serisi.index[anomali_maske].tolist(),
            'anomali_degerler': veri_serisi[anomali_maske].tolist(),
        }

        self.anomali_sonuclari['hareketli_ortalama'] = sonuc
        return sonuc

    # =========================================================================
    # 5. ANOMALİ RAPORU
    # =========================================================================

    def anomali_raporu(self) -> Dict[str, Any]:
        """
        Tüm yöntemlerin sonuçlarını birleştiren kapsamlı anomali raporu.
        
        Returns:
            Birleştirilmiş anomali raporu
        """
        if not self.anomali_sonuclari:
            logger.warning("Henüz anomali tespiti yapılmadı.")
            return {'uyari': 'Önce tespit yöntemlerinden birini çalıştırın.'}

        rapor = {
            'tarih': pd.Timestamp.now().isoformat(),
            'yontem_sayisi': len(self.anomali_sonuclari),
            'yontemler': {},
            'ozet': {},
        }

        toplam_anomali = 0
        for yontem, sonuc in self.anomali_sonuclari.items():
            rapor['yontemler'][yontem] = {
                'anomali_sayisi': sonuc['anomali_sayisi'],
                'anomali_orani': sonuc['anomali_orani'],
            }
            toplam_anomali += sonuc['anomali_sayisi']

        rapor['ozet'] = {
            'ortalama_anomali_orani': float(
                np.mean([s['anomali_orani'] for s in self.anomali_sonuclari.values()])
            ),
            'toplam_tespit': toplam_anomali,
            'en_cok_anomali_yontem': max(
                self.anomali_sonuclari.items(),
                key=lambda x: x[1]['anomali_sayisi']
            )[0],
        }

        return rapor
