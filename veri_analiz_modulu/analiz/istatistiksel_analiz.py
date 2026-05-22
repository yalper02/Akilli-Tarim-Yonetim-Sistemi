"""
İstatistiksel Analiz Modülü
============================

Bu modül, IoT sensörlerinden toplanan tarımsal verilere
istatistiksel analiz yöntemleri uygular.

Kullanılan Algoritmalar:
    - Betimsel İstatistik (Ortalama, Medyan, Standart Sapma, Çeyreklikler)
    - Korelasyon Analizi (Pearson, Spearman, Kendall)
    - Hipotez Testleri (t-test, ANOVA, Ki-Kare)
    - Regresyon Analizi (Doğrusal, Çoklu Doğrusal)
    - Zaman Bazlı İstatistikler (Hareketli Ortalama, Trend Analizi)

Kütüphaneler:
    - NumPy: Sayısal hesaplamalar
    - Pandas: Veri manipülasyonu
    - SciPy: İleri istatistiksel fonksiyonlar
"""

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import pearsonr, spearmanr, kendalltau
from typing import Dict, List, Tuple, Optional, Any
import logging

logger = logging.getLogger(__name__)


class IstatistikselAnalizci:
    """
    Tarımsal sensör verileri için istatistiksel analiz sınıfı.
    
    Bu sınıf, IoT sensörlerinden toplanan verilere çeşitli
    istatistiksel analiz yöntemlerini uygulayarak anlamlı
    çıkarımlar elde etmeyi sağlar.
    
    Kullanım Örneği:
        >>> analizci = IstatistikselAnalizci(veri_dataframe)
        >>> sonuclar = analizci.betimsel_istatistikler('toprak_nem')
        >>> korelasyon = analizci.korelasyon_analizi('toprak_nem', 'sicaklik')
    """

    def __init__(self, veri: pd.DataFrame):
        """
        Args:
            veri: Sensör verilerini içeren pandas DataFrame.
                  Beklenen sütunlar: sensor_tipi, deger, olcum_zamani
        """
        self.veri = veri.copy()
        self._veri_onislem()

    def _veri_onislem(self):
        """Veri ön işleme adımları: eksik veri, aykırı değer temizleme."""
        # Eksik değerlerin tespiti ve raporlanması
        eksik_sayisi = self.veri.isnull().sum().sum()
        if eksik_sayisi > 0:
            logger.warning(f"Veride {eksik_sayisi} eksik değer tespit edildi.")
            # Sayısal sütunlar için interpolasyon ile doldurma
            sayisal_sutunlar = self.veri.select_dtypes(include=[np.number]).columns
            self.veri[sayisal_sutunlar] = self.veri[sayisal_sutunlar].interpolate(
                method='linear', limit_direction='both'
            )

        # Tarih sütununun doğru formatta olduğundan emin ol
        if 'olcum_zamani' in self.veri.columns:
            self.veri['olcum_zamani'] = pd.to_datetime(self.veri['olcum_zamani'])

    # =========================================================================
    # 1. BETİMSEL İSTATİSTİK
    # =========================================================================

    def betimsel_istatistikler(self, sutun: str) -> Dict[str, float]:
        """
        Belirtilen sütun için kapsamlı betimsel istatistikleri hesaplar.
        
        Hesaplanan metrikler:
            - Ortalama (Mean)
            - Medyan (Median)
            - Standart Sapma (Std)
            - Varyans (Variance)
            - Minimum ve Maksimum
            - Çeyreklikler (Q1, Q2, Q3)
            - Çeyrekler Arası Aralık (IQR)
            - Çarpıklık (Skewness)
            - Basıklık (Kurtosis)
        
        Args:
            sutun: Analiz edilecek sütun adı
            
        Returns:
            İstatistik metrikleri içeren sözlük
        """
        veri_serisi = self.veri[sutun].dropna()

        q1 = veri_serisi.quantile(0.25)
        q2 = veri_serisi.quantile(0.50)
        q3 = veri_serisi.quantile(0.75)
        iqr = q3 - q1

        sonuclar = {
            'ortalama': float(veri_serisi.mean()),
            'medyan': float(veri_serisi.median()),
            'standart_sapma': float(veri_serisi.std()),
            'varyans': float(veri_serisi.var()),
            'minimum': float(veri_serisi.min()),
            'maksimum': float(veri_serisi.max()),
            'q1': float(q1),
            'q2_medyan': float(q2),
            'q3': float(q3),
            'iqr': float(iqr),
            'carpiklik': float(veri_serisi.skew()),
            'basiklik': float(veri_serisi.kurtosis()),
            'veri_sayisi': int(len(veri_serisi)),
            'standart_hata': float(veri_serisi.sem()),
        }

        logger.info(f"'{sutun}' sütunu için betimsel istatistikler hesaplandı.")
        return sonuclar

    def hareketli_ortalama(
        self, sutun: str, pencere_boyutu: int = 7
    ) -> pd.Series:
        """
        Hareketli ortalama hesaplar - trend analizi için kullanılır.
        
        Tarımsal uygulamada, sensör verilerindeki kısa vadeli
        dalgalanmaları düzeltmek ve uzun vadeli trendleri
        ortaya çıkarmak için kullanılır.
        
        Args:
            sutun: Analiz edilecek sütun adı
            pencere_boyutu: Hareketli ortalama pencere boyutu (gün)
            
        Returns:
            Hareketli ortalama değerlerini içeren pandas Series
        """
        return self.veri[sutun].rolling(window=pencere_boyutu, center=True).mean()

    def ustel_hareketli_ortalama(
        self, sutun: str, span: int = 7
    ) -> pd.Series:
        """
        Üstel Hareketli Ortalama (EMA) - Son değerlere daha fazla ağırlık verir.
        
        Args:
            sutun: Analiz edilecek sütun adı
            span: EMA periyodu
            
        Returns:
            EMA değerlerini içeren pandas Series
        """
        return self.veri[sutun].ewm(span=span, adjust=False).mean()

    # =========================================================================
    # 2. KORELASYON ANALİZİ
    # =========================================================================

    def korelasyon_analizi(
        self,
        sutun1: str,
        sutun2: str,
        yontem: str = 'pearson'
    ) -> Dict[str, Any]:
        """
        İki değişken arasındaki korelasyonu hesaplar.
        
        Tarımsal uygulamada korelasyon örnekleri:
            - Toprak nemi ↔ Sıcaklık (negatif korelasyon beklenir)
            - Yağış ↔ Toprak nemi (pozitif korelasyon)
            - Sıcaklık ↔ Buharlaşma (pozitif korelasyon)
        
        Args:
            sutun1: İlk değişkenin sütun adı
            sutun2: İkinci değişkenin sütun adı
            yontem: Korelasyon yöntemi ('pearson', 'spearman', 'kendall')
            
        Returns:
            Korelasyon katsayısı ve p-değerini içeren sözlük
        """
        veri1 = self.veri[sutun1].dropna()
        veri2 = self.veri[sutun2].dropna()

        # Ortak indeksler
        ortak_indeks = veri1.index.intersection(veri2.index)
        veri1 = veri1.loc[ortak_indeks]
        veri2 = veri2.loc[ortak_indeks]

        korelasyon_fonksiyonlari = {
            'pearson': pearsonr,
            'spearman': spearmanr,
            'kendall': kendalltau,
        }

        fonksiyon = korelasyon_fonksiyonlari.get(yontem, pearsonr)
        katsayi, p_degeri = fonksiyon(veri1, veri2)

        # Korelasyon gücünü yorumla
        guc = abs(katsayi)
        if guc < 0.3:
            yorum = "Zayıf korelasyon"
        elif guc < 0.7:
            yorum = "Orta düzeyde korelasyon"
        else:
            yorum = "Güçlü korelasyon"

        yon = "Pozitif" if katsayi > 0 else "Negatif"

        return {
            'yontem': yontem,
            'korelasyon_katsayisi': float(katsayi),
            'p_degeri': float(p_degeri),
            'istatistiksel_anlamlilik': p_degeri < 0.05,
            'yorum': f"{yon} {yorum.lower()}",
            'veri_sayisi': len(ortak_indeks),
        }

    def korelasyon_matrisi(self, sutunlar: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Çoklu değişkenler arasındaki korelasyon matrisini hesaplar.
        
        Args:
            sutunlar: Analiz edilecek sütun listesi (None ise tüm sayısal sütunlar)
            
        Returns:
            Korelasyon matrisini içeren DataFrame
        """
        if sutunlar:
            veri = self.veri[sutunlar]
        else:
            veri = self.veri.select_dtypes(include=[np.number])

        return veri.corr(method='pearson')

    # =========================================================================
    # 3. HİPOTEZ TESTLERİ
    # =========================================================================

    def t_test(
        self,
        grup1_verisi: pd.Series,
        grup2_verisi: pd.Series,
        esit_varyans: bool = True
    ) -> Dict[str, Any]:
        """
        İki grup arasındaki farkın istatistiksel anlamlılığını test eder.
        
        Tarımsal uygulama:
            Farklı sulama yöntemlerinin verimlilik üzerindeki
            etkisini karşılaştırmak için kullanılır.
        
        Args:
            grup1_verisi: İlk grubun verileri
            grup2_verisi: İkinci grubun verileri
            esit_varyans: Varyansların eşit olduğu varsayımı
            
        Returns:
            t-istatistiği, p-değeri ve yorumu içeren sözlük
        """
        t_istatistik, p_degeri = stats.ttest_ind(
            grup1_verisi.dropna(),
            grup2_verisi.dropna(),
            equal_var=esit_varyans
        )

        return {
            't_istatistik': float(t_istatistik),
            'p_degeri': float(p_degeri),
            'anlamli_fark': p_degeri < 0.05,
            'guven_duzeyi': 0.95,
            'yorum': (
                "İki grup arasında istatistiksel olarak anlamlı bir fark vardır."
                if p_degeri < 0.05
                else "İki grup arasında anlamlı bir fark bulunamamıştır."
            ),
        }

    def anova_testi(self, *gruplar: pd.Series) -> Dict[str, Any]:
        """
        Birden fazla grup arasındaki farkı test eder (Tek Yönlü ANOVA).
        
        Tarımsal uygulama:
            Farklı gübre tiplerinin bitki büyümesi üzerindeki
            etkisini karşılaştırmak için kullanılır.
        
        Args:
            *gruplar: Karşılaştırılacak grupların verileri
            
        Returns:
            F-istatistiği, p-değeri ve yorumu içeren sözlük
        """
        temiz_gruplar = [g.dropna() for g in gruplar]
        f_istatistik, p_degeri = stats.f_oneway(*temiz_gruplar)

        return {
            'f_istatistik': float(f_istatistik),
            'p_degeri': float(p_degeri),
            'grup_sayisi': len(gruplar),
            'anlamli_fark': p_degeri < 0.05,
            'yorum': (
                "Gruplar arasında istatistiksel olarak anlamlı bir fark vardır."
                if p_degeri < 0.05
                else "Gruplar arasında anlamlı bir fark bulunamamıştır."
            ),
        }

    # =========================================================================
    # 4. REGRESYON ANALİZİ
    # =========================================================================

    def dogrusal_regresyon(
        self, x_sutun: str, y_sutun: str
    ) -> Dict[str, Any]:
        """
        Basit Doğrusal Regresyon analizi.
        
        Tarımsal uygulama:
            Sıcaklık ile toprak nemi arasındaki ilişkiyi modellemek,
            sulama miktarı ile ürün verimi arasındaki ilişkiyi tahmin etmek.
        
        Args:
            x_sutun: Bağımsız değişken sütun adı
            y_sutun: Bağımlı değişken sütun adı
            
        Returns:
            Regresyon katsayıları ve model metrikleri
        """
        x = self.veri[x_sutun].dropna()
        y = self.veri[y_sutun].dropna()
        ortak = x.index.intersection(y.index)
        x, y = x.loc[ortak], y.loc[ortak]

        egim, kesisim, r_degeri, p_degeri, std_hata = stats.linregress(x, y)
        r_kare = r_degeri ** 2

        # Tahmin değerlerini hesapla
        y_tahmin = egim * x + kesisim
        artik = y - y_tahmin

        return {
            'egim': float(egim),
            'kesisim': float(kesisim),
            'r_degeri': float(r_degeri),
            'r_kare': float(r_kare),
            'p_degeri': float(p_degeri),
            'standart_hata': float(std_hata),
            'denklem': f"y = {egim:.4f}x + {kesisim:.4f}",
            'artik_ortalama': float(artik.mean()),
            'artik_std': float(artik.std()),
            'yorum': (
                f"Model, bağımlı değişkendeki varyansın %{r_kare*100:.1f}'ini açıklamaktadır. "
                f"{'Güçlü' if r_kare > 0.7 else 'Orta' if r_kare > 0.3 else 'Zayıf'} "
                f"bir doğrusal ilişki mevcuttur."
            ),
        }

    # =========================================================================
    # 5. AYKIRI DEĞER TESPİTİ
    # =========================================================================

    def aykiri_deger_tespiti(
        self, sutun: str, yontem: str = 'iqr'
    ) -> Dict[str, Any]:
        """
        Aykırı değerleri tespit eder.
        
        Tarımsal uygulamada sensör arızaları veya olağandışı
        hava koşulları nedeniyle oluşan aykırı değerleri tespit eder.
        
        Args:
            sutun: Analiz edilecek sütun
            yontem: Tespit yöntemi ('iqr' veya 'zscore')
            
        Returns:
            Aykırı değer bilgileri ve temizlenmiş veri
        """
        veri_serisi = self.veri[sutun].dropna()

        if yontem == 'iqr':
            q1 = veri_serisi.quantile(0.25)
            q3 = veri_serisi.quantile(0.75)
            iqr = q3 - q1
            alt_sinir = q1 - 1.5 * iqr
            ust_sinir = q3 + 1.5 * iqr
            aykiri_maske = (veri_serisi < alt_sinir) | (veri_serisi > ust_sinir)
        elif yontem == 'zscore':
            z_skorlar = np.abs(stats.zscore(veri_serisi))
            alt_sinir = veri_serisi.mean() - 3 * veri_serisi.std()
            ust_sinir = veri_serisi.mean() + 3 * veri_serisi.std()
            aykiri_maske = z_skorlar > 3
        else:
            raise ValueError(f"Geçersiz yöntem: {yontem}")

        aykiri_degerler = veri_serisi[aykiri_maske]

        return {
            'yontem': yontem,
            'toplam_veri': len(veri_serisi),
            'aykiri_deger_sayisi': int(aykiri_maske.sum()),
            'aykiri_oran': float(aykiri_maske.sum() / len(veri_serisi) * 100),
            'alt_sinir': float(alt_sinir),
            'ust_sinir': float(ust_sinir),
            'aykiri_degerler': aykiri_degerler.tolist(),
            'temiz_ortalama': float(veri_serisi[~aykiri_maske].mean()),
            'kirli_ortalama': float(veri_serisi.mean()),
        }

    # =========================================================================
    # 6. TOPLU ANALİZ RAPORU
    # =========================================================================

    def toplu_rapor_olustur(self, sutunlar: List[str]) -> Dict[str, Any]:
        """
        Belirtilen sütunlar için kapsamlı bir analiz raporu oluşturur.
        
        Args:
            sutunlar: Analiz edilecek sütun listesi
            
        Returns:
            Her sütun için betimsel istatistikler, korelasyonlar ve
            aykırı değer bilgilerini içeren kapsamlı rapor
        """
        rapor = {
            'betimsel_istatistikler': {},
            'korelasyon_matrisi': None,
            'aykiri_degerler': {},
        }

        for sutun in sutunlar:
            if sutun in self.veri.columns:
                rapor['betimsel_istatistikler'][sutun] = \
                    self.betimsel_istatistikler(sutun)
                rapor['aykiri_degerler'][sutun] = \
                    self.aykiri_deger_tespiti(sutun)

        rapor['korelasyon_matrisi'] = \
            self.korelasyon_matrisi(sutunlar).to_dict()

        logger.info(f"{len(sutunlar)} sütun için toplu rapor oluşturuldu.")
        return rapor
