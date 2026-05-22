"""
Veri Görselleştirme Modülü
============================

Bu modül, tarımsal IoT sensör verilerinin görselleştirilmesini sağlar.
Hem statik grafikler (Matplotlib/Seaborn) hem de interaktif grafikler
(Plotly) oluşturur.

Kullanılan Kütüphaneler:
    1. Matplotlib: Temel grafik kütüphanesi
        - Çizgi grafikleri, histogram, scatter plot
        - Yüksek kalite statik grafikler
        - PDF/PNG çıktı desteği
    
    2. Seaborn: İstatistiksel görselleştirme
        - Isı haritaları (korelasyon matrisi)
        - Kutu grafikleri (box plot)
        - Violin grafikleri
        - Pair plot (çoklu değişken ilişkileri)
    
    3. Plotly: İnteraktif web grafikleri
        - Gerçek zamanlı dashboard grafikleri
        - Zoom, pan, hover desteği
        - Django template'lerinde gömülebilir HTML çıktısı

Görselleştirme Teknikleri:
    - Zaman serisi grafikleri: Sensör verisi trendi
    - Isı haritaları: Bölgesel sıcaklık/nem dağılımı
    - Scatter plot: Değişkenler arası ilişki
    - Box plot: Veri dağılımı ve aykırı değerler
    - Gauge grafikleri: Anlık sensör durumu
    - Coğrafi haritalar: Sensör konum dağılımı
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
import logging
import os
import io
import base64

import matplotlib
matplotlib.use('Agg')  # GUI olmadan grafik oluşturma (sunucu ortamı)
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
import seaborn as sns

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.io as pio

logger = logging.getLogger(__name__)

# Matplotlib stil ayarları
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Türkçe karakter desteği
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False


class GrafikOlusturucu:
    """
    Tarımsal veri görselleştirme sınıfı.
    
    Bu sınıf, sensör verilerini çeşitli grafik formatlarında
    görselleştirerek veri analizi sonuçlarının anlaşılmasını kolaylaştırır.
    
    Çıktı Formatları:
        - PNG/JPG: Statik görüntü dosyaları
        - HTML: İnteraktif web grafikleri (Plotly)
        - Base64: Django template'lere gömme için
        - JSON: Plotly grafik verisi (AJAX ile yükleme)
    
    Kullanım Örneği:
        >>> grafik = GrafikOlusturucu(kayit_dizini='/media/grafikler/')
        >>> grafik.zaman_serisi_grafigi(veri, 'Toprak Nemi', 'toprak_nem')
        >>> html = grafik.interaktif_dashboard(sensor_verileri)
    """

    # Sensör tiplerine göre renk paleti
    SENSOR_RENKLERI = {
        'toprak_nem': '#2196F3',     # Mavi
        'sicaklik': '#FF5722',       # Kırmızı-Turuncu
        'hava_nem': '#4CAF50',       # Yeşil
        'isik': '#FFC107',           # Sarı
        'ph': '#9C27B0',             # Mor
        'ruzgar': '#607D8B',         # Gri-Mavi
        'yagis': '#00BCD4',          # Cyan
        'ec': '#795548',             # Kahverengi
    }

    # Sensör birim bilgileri
    SENSOR_BIRIMLERI = {
        'toprak_nem': '%',
        'sicaklik': '°C',
        'hava_nem': '%',
        'isik': 'lux',
        'ph': 'pH',
        'ruzgar': 'km/h',
        'yagis': 'mm',
        'ec': 'mS/cm',
    }

    def __init__(self, kayit_dizini: Optional[str] = None, dpi: int = 150):
        """
        Args:
            kayit_dizini: Grafiklerin kaydedileceği dizin
            dpi: Grafik çözünürlüğü (dots per inch)
        """
        self.kayit_dizini = kayit_dizini
        self.dpi = dpi

        if kayit_dizini and not os.path.exists(kayit_dizini):
            os.makedirs(kayit_dizini, exist_ok=True)

    def _grafik_kaydet(
        self, fig: Figure, dosya_adi: str, format: str = 'png'
    ) -> Optional[str]:
        """Grafiği dosyaya kaydeder."""
        if self.kayit_dizini:
            yol = os.path.join(self.kayit_dizini, f"{dosya_adi}.{format}")
            fig.savefig(yol, dpi=self.dpi, bbox_inches='tight',
                        facecolor='white', edgecolor='none')
            logger.info(f"Grafik kaydedildi: {yol}")
            return yol
        return None

    def _grafik_base64(self, fig: Figure) -> str:
        """Grafiği Base64 string'e dönüştürür (Django template'e gömme için)."""
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=self.dpi,
                    bbox_inches='tight', facecolor='white')
        buffer.seek(0)
        img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close(fig)
        return f"data:image/png;base64,{img_str}"

    # =========================================================================
    # 1. ZAMAN SERİSİ GRAFİKLERİ (Matplotlib)
    # =========================================================================

    def zaman_serisi_grafigi(
        self,
        veri: pd.DataFrame,
        baslik: str,
        deger_sutunu: str,
        zaman_sutunu: str = 'olcum_zamani',
        hareketli_ort: bool = True,
        pencere: int = 7,
        kaydet: bool = True
    ) -> str:
        """
        Zaman serisi çizgi grafiği oluşturur.
        
        Özellikler:
            - Ana veri çizgisi
            - Hareketli ortalama çizgisi (opsiyonel)
            - Tarih formatlı x ekseni
            - Otomatik renk seçimi
        
        Args:
            veri: Sensör veri DataFrame'i
            baslik: Grafik başlığı
            deger_sutunu: Değer sütunu adı
            zaman_sutunu: Zaman sütunu adı
            hareketli_ort: Hareketli ortalama çizgisi ekle
            pencere: Hareketli ortalama pencere boyutu
            kaydet: Dosyaya kaydet
            
        Returns:
            Base64 kodlanmış grafik veya dosya yolu
        """
        fig, ax = plt.subplots(figsize=(14, 6))

        renk = self.SENSOR_RENKLERI.get(deger_sutunu, '#333333')
        birim = self.SENSOR_BIRIMLERI.get(deger_sutunu, '')

        # Ana veri
        ax.plot(
            veri[zaman_sutunu], veri[deger_sutunu],
            color=renk, alpha=0.6, linewidth=1,
            label=f'{baslik} (Ham Veri)'
        )

        # Hareketli ortalama
        if hareketli_ort:
            ha = veri[deger_sutunu].rolling(window=pencere, center=True).mean()
            ax.plot(
                veri[zaman_sutunu], ha,
                color=renk, linewidth=2.5,
                label=f'{pencere} Günlük Hareketli Ortalama'
            )

        ax.set_title(baslik, fontsize=16, fontweight='bold', pad=15)
        ax.set_xlabel('Tarih', fontsize=12)
        ax.set_ylabel(f'Değer ({birim})', fontsize=12)
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(True, alpha=0.3)

        # Tarih formatı
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        fig.autofmt_xdate()

        plt.tight_layout()

        if kaydet:
            self._grafik_kaydet(fig, f"zaman_serisi_{deger_sutunu}")

        return self._grafik_base64(fig)

    def coklu_sensor_grafigi(
        self,
        veri: pd.DataFrame,
        sensor_sutunlari: List[str],
        zaman_sutunu: str = 'olcum_zamani',
        baslik: str = 'Çoklu Sensör Verileri'
    ) -> str:
        """
        Birden fazla sensör verisini alt alta grafiklerle gösterir.
        
        Args:
            veri: Sensör veri DataFrame'i
            sensor_sutunlari: Gösterilecek sensör sütunları
            zaman_sutunu: Zaman sütunu
            baslik: Ana başlık
            
        Returns:
            Base64 kodlanmış grafik
        """
        n = len(sensor_sutunlari)
        fig, axes = plt.subplots(n, 1, figsize=(14, 4 * n), sharex=True)

        if n == 1:
            axes = [axes]

        for i, sutun in enumerate(sensor_sutunlari):
            renk = self.SENSOR_RENKLERI.get(sutun, '#333333')
            birim = self.SENSOR_BIRIMLERI.get(sutun, '')

            axes[i].plot(veri[zaman_sutunu], veri[sutun],
                         color=renk, linewidth=1.5, alpha=0.8)
            axes[i].fill_between(veri[zaman_sutunu], veri[sutun],
                                 alpha=0.1, color=renk)
            axes[i].set_ylabel(f'{sutun}\n({birim})', fontsize=10)
            axes[i].grid(True, alpha=0.3)
            axes[i].set_title(sutun.replace('_', ' ').title(),
                              fontsize=12, fontweight='bold')

        axes[-1].xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
        fig.suptitle(baslik, fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()

        return self._grafik_base64(fig)

    # =========================================================================
    # 2. İSTATİSTİKSEL GRAFİKLER (Seaborn)
    # =========================================================================

    def korelasyon_isi_haritasi(
        self,
        korelasyon_matrisi: pd.DataFrame,
        baslik: str = 'Sensör Verileri Korelasyon Matrisi'
    ) -> str:
        """
        Korelasyon matrisi ısı haritası oluşturur (Seaborn).
        
        Tarımsal kullanım:
            Hangi sensör verilerinin birbiriyle ilişkili olduğunu
            görsel olarak analiz etmek için kullanılır.
        
        Args:
            korelasyon_matrisi: Korelasyon DataFrame'i
            baslik: Grafik başlığı
            
        Returns:
            Base64 kodlanmış ısı haritası
        """
        fig, ax = plt.subplots(figsize=(10, 8))

        maske = np.triu(np.ones_like(korelasyon_matrisi, dtype=bool))

        sns.heatmap(
            korelasyon_matrisi,
            mask=maske,
            annot=True,
            fmt='.2f',
            cmap='RdBu_r',
            center=0,
            vmin=-1, vmax=1,
            square=True,
            linewidths=0.5,
            cbar_kws={'shrink': 0.8, 'label': 'Korelasyon Katsayısı'},
            ax=ax
        )

        ax.set_title(baslik, fontsize=14, fontweight='bold', pad=15)
        plt.tight_layout()

        return self._grafik_base64(fig)

    def kutu_grafigi(
        self,
        veri: pd.DataFrame,
        sutunlar: List[str],
        baslik: str = 'Sensör Veri Dağılımları'
    ) -> str:
        """
        Kutu grafiği (Box Plot) - Veri dağılımını ve aykırı değerleri gösterir.
        
        Box Plot yorumlama:
            - Kutu: Q1-Q3 aralığı (verilerin %50'si)
            - Orta çizgi: Medyan
            - Bıyıklar: 1.5×IQR sınırları
            - Noktalar: Aykırı değerler
        
        Args:
            veri: Veri DataFrame'i
            sutunlar: Gösterilecek sütunlar
            baslik: Grafik başlığı
            
        Returns:
            Base64 kodlanmış grafik
        """
        fig, ax = plt.subplots(figsize=(12, 6))

        renkler = [self.SENSOR_RENKLERI.get(s, '#666') for s in sutunlar]

        bp = ax.boxplot(
            [veri[s].dropna() for s in sutunlar],
            labels=[s.replace('_', ' ').title() for s in sutunlar],
            patch_artist=True,
            notch=True,
            showfliers=True
        )

        for patch, renk in zip(bp['boxes'], renkler):
            patch.set_facecolor(renk)
            patch.set_alpha(0.6)

        ax.set_title(baslik, fontsize=14, fontweight='bold')
        ax.set_ylabel('Değer', fontsize=12)
        ax.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()

        return self._grafik_base64(fig)

    def dagilim_grafigi(
        self,
        veri: pd.Series,
        baslik: str,
        bins: int = 50
    ) -> str:
        """
        Histogram ve KDE (Kernel Density Estimation) grafiği.
        
        Veri dağılımının normal dağılıma uyup uymadığını görsel
        olarak değerlendirmek için kullanılır.
        
        Args:
            veri: Veri serisi
            baslik: Grafik başlığı
            bins: Histogram kutusu sayısı
            
        Returns:
            Base64 kodlanmış grafik
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        sns.histplot(veri.dropna(), bins=bins, kde=True, color='#2196F3',
                     alpha=0.6, ax=ax, stat='density')

        # Normal dağılım eğrisi
        mu, sigma = veri.mean(), veri.std()
        x = np.linspace(veri.min(), veri.max(), 100)
        from scipy.stats import norm
        ax.plot(x, norm.pdf(x, mu, sigma), 'r--', linewidth=2,
                label=f'Normal Dağılım (μ={mu:.2f}, σ={sigma:.2f})')

        ax.set_title(baslik, fontsize=14, fontweight='bold')
        ax.set_xlabel('Değer', fontsize=12)
        ax.set_ylabel('Yoğunluk', fontsize=12)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()

        return self._grafik_base64(fig)

    def pair_plot(
        self,
        veri: pd.DataFrame,
        sutunlar: List[str],
        baslik: str = 'Değişkenler Arası İlişkiler'
    ) -> str:
        """
        Pair Plot - Tüm değişken çiftleri arasındaki ilişkileri gösterir.
        
        Her hücrede:
            - Köşegen: Her değişkenin kendi dağılımı (KDE)
            - Diğer hücreler: İki değişken arası scatter plot
        
        Args:
            veri: Veri DataFrame'i
            sutunlar: Gösterilecek sütunlar
            baslik: Grafik başlığı
            
        Returns:
            Base64 kodlanmış grafik
        """
        g = sns.pairplot(
            veri[sutunlar].dropna(),
            diag_kind='kde',
            plot_kws={'alpha': 0.5, 's': 20},
            diag_kws={'fill': True}
        )
        g.fig.suptitle(baslik, y=1.02, fontsize=14, fontweight='bold')

        buffer = io.BytesIO()
        g.fig.savefig(buffer, format='png', dpi=self.dpi, bbox_inches='tight')
        buffer.seek(0)
        img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close(g.fig)
        return f"data:image/png;base64,{img_str}"

    # =========================================================================
    # 3. İNTERAKTİF GRAFİKLER (Plotly)
    # =========================================================================

    def interaktif_zaman_serisi(
        self,
        veri: pd.DataFrame,
        deger_sutunu: str,
        zaman_sutunu: str = 'olcum_zamani',
        baslik: str = 'Sensör Verisi',
        anomali_indeksler: Optional[List] = None
    ) -> str:
        """
        Plotly ile interaktif zaman serisi grafiği oluşturur.
        
        Özellikler:
            - Zoom in/out, pan, hover tooltip
            - Range slider ile tarih aralığı seçimi
            - Anomali noktaları kırmızı ile işaretlenir
            - Django template'e HTML olarak gömülebilir
        
        Args:
            veri: Sensör veri DataFrame'i
            deger_sutunu: Değer sütunu
            zaman_sutunu: Zaman sütunu
            baslik: Grafik başlığı
            anomali_indeksler: Anomali olarak işaretlenecek indeksler
            
        Returns:
            Plotly HTML string (template'e gömülebilir)
        """
        renk = self.SENSOR_RENKLERI.get(deger_sutunu, '#2196F3')
        birim = self.SENSOR_BIRIMLERI.get(deger_sutunu, '')

        fig = go.Figure()

        # Ana veri çizgisi
        fig.add_trace(go.Scatter(
            x=veri[zaman_sutunu],
            y=veri[deger_sutunu],
            mode='lines',
            name='Sensör Verisi',
            line=dict(color=renk, width=1.5),
            fill='tonexty',
            fillcolor=f'rgba({int(renk[1:3],16)},{int(renk[3:5],16)},{int(renk[5:7],16)},0.1)',
            hovertemplate=(
                '<b>Tarih:</b> %{x|%d/%m/%Y %H:%M}<br>'
                f'<b>Değer:</b> %{{y:.2f}} {birim}<br>'
                '<extra></extra>'
            ),
        ))

        # Anomali noktalarını işaretle
        if anomali_indeksler:
            anomali_veri = veri.loc[anomali_indeksler]
            fig.add_trace(go.Scatter(
                x=anomali_veri[zaman_sutunu],
                y=anomali_veri[deger_sutunu],
                mode='markers',
                name='Anomali',
                marker=dict(
                    color='red', size=10, symbol='x',
                    line=dict(width=2, color='darkred')
                ),
                hovertemplate=(
                    '<b>⚠️ ANOMALİ</b><br>'
                    '<b>Tarih:</b> %{x|%d/%m/%Y %H:%M}<br>'
                    f'<b>Değer:</b> %{{y:.2f}} {birim}<br>'
                    '<extra></extra>'
                ),
            ))

        fig.update_layout(
            title=dict(text=baslik, font=dict(size=18)),
            xaxis=dict(
                title='Tarih',
                rangeslider=dict(visible=True),
                type='date',
            ),
            yaxis=dict(title=f'Değer ({birim})'),
            template='plotly_white',
            hovermode='x unified',
            height=500,
            margin=dict(l=60, r=30, t=60, b=40),
        )

        return pio.to_html(fig, full_html=False, include_plotlyjs='cdn')

    def interaktif_dashboard(
        self,
        veri: pd.DataFrame,
        sensor_sutunlari: List[str],
        zaman_sutunu: str = 'olcum_zamani'
    ) -> str:
        """
        Çoklu sensör verilerini gösteren interaktif dashboard.
        
        Dashboard bileşenleri:
            - Her sensör için ayrı zaman serisi grafiği
            - Ortak zaman ekseni ile senkronize zoom
            - Hover ile detaylı bilgi
        
        Args:
            veri: Sensör verileri
            sensor_sutunlari: Dashboard'da gösterilecek sensör sütunları
            zaman_sutunu: Zaman sütunu
            
        Returns:
            Plotly HTML dashboard string
        """
        n = len(sensor_sutunlari)
        basliklar = [s.replace('_', ' ').title() for s in sensor_sutunlari]

        fig = make_subplots(
            rows=n, cols=1,
            subplot_titles=basliklar,
            shared_xaxes=True,
            vertical_spacing=0.05,
        )

        for i, sutun in enumerate(sensor_sutunlari, 1):
            renk = self.SENSOR_RENKLERI.get(sutun, '#333')
            birim = self.SENSOR_BIRIMLERI.get(sutun, '')

            fig.add_trace(
                go.Scatter(
                    x=veri[zaman_sutunu],
                    y=veri[sutun],
                    mode='lines',
                    name=basliklar[i - 1],
                    line=dict(color=renk, width=1.5),
                    hovertemplate=f'%{{y:.2f}} {birim}<extra></extra>',
                ),
                row=i, col=1
            )

            fig.update_yaxes(
                title_text=f'{birim}',
                row=i, col=1
            )

        fig.update_layout(
            title='Akıllı Tarım - Sensör Verileri Dashboard',
            height=300 * n,
            template='plotly_white',
            showlegend=True,
            hovermode='x unified',
        )

        # Son grafiğe range slider ekle
        fig.update_xaxes(rangeslider_visible=True, row=n, col=1)

        return pio.to_html(fig, full_html=False, include_plotlyjs='cdn')

    def gauge_grafigi(
        self,
        deger: float,
        baslik: str,
        birim: str = '',
        min_deger: float = 0,
        max_deger: float = 100,
        esik_degerleri: Optional[Dict[str, float]] = None
    ) -> str:
        """
        Gauge (gösterge) grafiği - Anlık sensör durumu için.
        
        Tarımsal kullanım:
            - Anlık toprak nemi seviyesi
            - Sıcaklık göstergesi
            - pH seviyesi
        
        Args:
            deger: Gösterilecek değer
            baslik: Başlık
            birim: Birim
            min_deger: Minimum skala değeri
            max_deger: Maksimum skala değeri
            esik_degerleri: Renk eşik değerleri {'dusuk': 30, 'yuksek': 70}
            
        Returns:
            Plotly HTML gauge grafiği
        """
        if esik_degerleri is None:
            esik_degerleri = {
                'dusuk': max_deger * 0.3,
                'yuksek': max_deger * 0.7,
            }

        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=deger,
            title={'text': f"{baslik} ({birim})", 'font': {'size': 18}},
            number={'suffix': f' {birim}', 'font': {'size': 28}},
            gauge={
                'axis': {'range': [min_deger, max_deger], 'tickwidth': 1},
                'bar': {'color': "#1976D2"},
                'bgcolor': "white",
                'borderwidth': 2,
                'steps': [
                    {'range': [min_deger, esik_degerleri['dusuk']], 'color': '#FFCDD2'},
                    {'range': [esik_degerleri['dusuk'], esik_degerleri['yuksek']], 'color': '#C8E6C9'},
                    {'range': [esik_degerleri['yuksek'], max_deger], 'color': '#FFCDD2'},
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': deger
                }
            }
        ))

        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=50, b=20),
            template='plotly_white',
        )

        return pio.to_html(fig, full_html=False, include_plotlyjs='cdn')

    def scatter_plot_interaktif(
        self,
        veri: pd.DataFrame,
        x_sutun: str,
        y_sutun: str,
        renk_sutunu: Optional[str] = None,
        baslik: str = 'Scatter Plot'
    ) -> str:
        """
        İnteraktif scatter plot (saçılım grafiği).
        
        İki değişken arasındaki ilişkiyi görselleştirir.
        Opsiyonel olarak üçüncü bir değişkenle renklendirme yapılabilir.
        
        Args:
            veri: Veri DataFrame'i
            x_sutun: X ekseni sütunu
            y_sutun: Y ekseni sütunu
            renk_sutunu: Renklendirme sütunu (opsiyonel)
            baslik: Grafik başlığı
            
        Returns:
            Plotly HTML string
        """
        fig = px.scatter(
            veri,
            x=x_sutun,
            y=y_sutun,
            color=renk_sutunu,
            title=baslik,
            labels={
                x_sutun: x_sutun.replace('_', ' ').title(),
                y_sutun: y_sutun.replace('_', ' ').title(),
            },
            template='plotly_white',
            opacity=0.6,
            trendline='ols',  # Doğrusal trend çizgisi
        )

        fig.update_layout(height=500)
        return pio.to_html(fig, full_html=False, include_plotlyjs='cdn')

    def anomali_gorsellestirme(
        self,
        veri: pd.DataFrame,
        deger_sutunu: str,
        zaman_sutunu: str,
        anomali_maske: pd.Series,
        baslik: str = 'Anomali Tespiti Sonuçları'
    ) -> str:
        """
        Anomali tespiti sonuçlarını görselleştirir.
        
        Normal veriler mavi, anomaliler kırmızı ile gösterilir.
        Güven aralığı band olarak arka planda gösterilir.
        
        Args:
            veri: Sensör veri DataFrame'i
            deger_sutunu: Değer sütunu
            zaman_sutunu: Zaman sütunu
            anomali_maske: Anomali boolean mask
            baslik: Grafik başlığı
            
        Returns:
            Plotly HTML string
        """
        fig = go.Figure()

        # Normal veriler
        normal_veri = veri[~anomali_maske]
        fig.add_trace(go.Scatter(
            x=normal_veri[zaman_sutunu],
            y=normal_veri[deger_sutunu],
            mode='lines',
            name='Normal Veri',
            line=dict(color='#2196F3', width=1),
        ))

        # Anomali noktaları
        anomali_veri = veri[anomali_maske]
        fig.add_trace(go.Scatter(
            x=anomali_veri[zaman_sutunu],
            y=anomali_veri[deger_sutunu],
            mode='markers',
            name='Anomali',
            marker=dict(color='red', size=8, symbol='circle',
                        line=dict(width=1, color='darkred')),
        ))

        # İstatistik bantları
        ort = veri[deger_sutunu].mean()
        std = veri[deger_sutunu].std()

        fig.add_hline(y=ort, line_dash="dash", line_color="green",
                      annotation_text=f"Ortalama: {ort:.2f}")
        fig.add_hrect(y0=ort - 2 * std, y1=ort + 2 * std,
                      fillcolor="green", opacity=0.05,
                      annotation_text="±2σ Güven Aralığı")

        fig.update_layout(
            title=baslik,
            xaxis_title='Tarih',
            yaxis_title='Değer',
            template='plotly_white',
            height=500,
            hovermode='x unified',
        )

        return pio.to_html(fig, full_html=False, include_plotlyjs='cdn')
