# 📊 Veri Toplama ve Analiz Modülü - Teknik Dokümantasyon

## Akıllı Tarım Yönetim Sistemi

> Bu doküman, IoT sensör verilerinin toplanması, analiz edilmesi ve görselleştirilmesi 
> için kullanılan algoritma, kütüphane ve teknikleri detaylı olarak açıklamaktadır.

---

## 📋 İçindekiler

1. [Modül Mimarisi](#1-modül-mimarisi)
2. [Veri Analiz Algoritmaları](#2-veri-analiz-algoritmaları)
3. [Makine Öğrenmesi Algoritmaları](#3-makine-öğrenmesi-algoritmaları)
4. [Zaman Serisi Analiz Yöntemleri](#4-zaman-serisi-analiz-yöntemleri)
5. [Anomali Tespit Algoritmaları](#5-anomali-tespit-algoritmaları)
6. [Veri Görselleştirme Kütüphaneleri ve Teknikleri](#6-veri-görselleştirme-kütüphaneleri-ve-teknikleri)
7. [Python ve Django Entegrasyonu](#7-python-ve-django-entegrasyonu)
8. [Kullanılan Kütüphaneler Özeti](#8-kullanılan-kütüphaneler-özeti)

---

## 1. Modül Mimarisi

```
veri_analiz_modulu/
├── analiz/                          # Analiz Algoritmaları
│   ├── istatistiksel_analiz.py      # İstatistiksel yöntemler
│   ├── makine_ogrenmesi.py          # ML algoritmaları
│   ├── zaman_serisi_analiz.py       # Zaman serisi modelleri
│   └── anomali_tespiti.py           # Anomali tespit yöntemleri
│
├── gorsellestirme/                  # Görselleştirme
│   └── grafik_olusturucu.py         # Matplotlib, Seaborn, Plotly
│
├── entegrasyon/                     # Django Entegrasyon Kılavuzu
│   └── django_entegrasyon.py
│
├── templates/veri_analiz/           # Django HTML Şablonları
│   └── dashboard.html
│
├── management/commands/             # Django Yönetim Komutları
│   └── ornek_veri_olustur.py
│
├── models.py                        # Veritabanı Modelleri
├── views.py                         # Django View'ları ve API'ler
├── urls.py                          # URL Yapılandırması
├── admin.py                         # Admin Panel Kayıtları
├── signals.py                       # Otomatik Tetikleyiciler
└── requirements.txt                 # Bağımlılıklar
```

### Veri Akış Diyagramı

```
IoT Sensörler ──→ Django API ──→ Veritabanı (PostgreSQL/SQLite)
                                      │
                                      ▼
                              ┌──────────────┐
                              │  Veri İşleme  │
                              │   (Pandas)    │
                              └──────┬───────┘
                                     │
                    ┌────────────────┼────────────────┐
                    ▼                ▼                ▼
            ┌──────────┐    ┌──────────────┐  ┌─────────────┐
            │İstatistik│    │   Makine     │  │  Zaman      │
            │ Analiz   │    │  Öğrenmesi   │  │  Serisi     │
            │ (SciPy)  │    │(Scikit-learn)│  │(Statsmodels)│
            └────┬─────┘    └──────┬───────┘  └──────┬──────┘
                 │                 │                  │
                 └────────────────┼──────────────────┘
                                  ▼
                        ┌──────────────────┐
                        │  Görselleştirme  │
                        │ Matplotlib/Plotly│
                        └────────┬─────────┘
                                 ▼
                         Django Dashboard
```

---

## 2. Veri Analiz Algoritmaları

### 2.1 Betimsel İstatistik

Sensör verilerinin temel özelliklerini özetlemek için kullanılır.

| Metrik | Açıklama | Tarımsal Uygulama |
|--------|----------|-------------------|
| **Ortalama (Mean)** | Tüm değerlerin aritmetik ortalaması | Bölgenin ortalama toprak nemi |
| **Medyan** | Sıralı değerlerin ortasındaki değer | Aykırı değerlerden etkilenmeyen merkezi ölçü |
| **Standart Sapma** | Değerlerin ortalamadan sapma ölçüsü | Sensör ölçüm kararlılığı |
| **Çeyreklikler (Q1, Q3)** | Verinin %25 ve %75'lik dilimleri | Normal çalışma aralığı tespiti |
| **IQR** | Q3 - Q1 (Çeyrekler arası aralık) | Aykırı değer tespiti eşiği |
| **Çarpıklık (Skewness)** | Dağılımın simetri ölçüsü | Veri dağılım şekli analizi |
| **Basıklık (Kurtosis)** | Dağılımın sivriliği | Uç değer yoğunluğu |

**Kullanılan Fonksiyon:** `IstatistikselAnalizci.betimsel_istatistikler()`

### 2.2 Korelasyon Analizi

İki veya daha fazla değişken arasındaki ilişkinin gücünü ve yönünü ölçer.

| Yöntem | Kullanım Durumu | Aralık |
|--------|----------------|--------|
| **Pearson** | Doğrusal ilişki ölçümü | [-1, +1] |
| **Spearman** | Sıralama bazlı ilişki (doğrusal olması gerekmez) | [-1, +1] |
| **Kendall** | Küçük veri setleri, sıralama korelasyonu | [-1, +1] |

**Tarımsal Korelasyon Örnekleri:**
- Toprak Nemi ↔ Sıcaklık: Negatif korelasyon (sıcaklık arttıkça nem düşer)
- Yağış ↔ Toprak Nemi: Pozitif korelasyon
- Işık Yoğunluğu ↔ Sıcaklık: Pozitif korelasyon

### 2.3 Hipotez Testleri

| Test | Amaç | Tarımsal Uygulama |
|------|-------|-------------------|
| **t-Test** | İki grup ortalamasını karşılaştırma | Sulanan vs. sulanmayan alanlar arasındaki fark |
| **ANOVA** | Üç+ grup karşılaştırma | Farklı gübre tiplerinin verime etkisi |
| **Ki-Kare** | Kategorik değişken ilişkisi | Toprak tipi ve hastalık görülme sıklığı |

### 2.4 Doğrusal Regresyon

```
y = β₀ + β₁x + ε

Burada:
  y  = Bağımlı değişken (örn: sulama ihtiyacı)
  x  = Bağımsız değişken (örn: toprak nemi)
  β₀ = Kesişim noktası
  β₁ = Eğim katsayısı
  ε  = Hata terimi
```

**Değerlendirme Metrikleri:**
- **R² (Belirtme katsayısı):** Modelin açıkladığı varyans oranı
- **p-değeri:** İstatistiksel anlamlılık (< 0.05 ise anlamlı)
- **Standart Hata:** Tahmin doğruluğu ölçüsü

---

## 3. Makine Öğrenmesi Algoritmaları

### 3.1 Gözetimli Öğrenme (Supervised Learning)

#### Random Forest (Rastgele Orman)

```
Çalışma Prensibi:
  1. Veriden rastgele alt kümeler seçilir (Bootstrap)
  2. Her alt küme için bir karar ağacı eğitilir
  3. Tüm ağaçların tahminleri birleştirilir (oylama/ortalama)

Avantajları:
  ✓ Overfitting'e karşı dayanıklı
  ✓ Özellik önemi hesaplayabilir
  ✓ Eksik verilere toleranslı
  ✓ Hem sınıflandırma hem regresyon yapabilir

Tarımsal Kullanım:
  → Toprak nemi tahmini
  → Sulama ihtiyacı sınıflandırması
  → Verim tahmini
```

#### Gradient Boosting

```
Çalışma Prensibi:
  1. Zayıf bir model eğitilir
  2. Hataları düzeltmek için yeni bir model eklenir
  3. Bu süreç iteratif olarak tekrarlanır
  4. Son model, tüm zayıf modellerin ağırlıklı toplamıdır

Avantajları:
  ✓ Genellikle en yüksek doğruluk
  ✓ Farklı kayıp fonksiyonları kullanılabilir
  ✓ Karmaşık ilişkileri modelleyebilir

Tarımsal Kullanım:
  → Hassas verim tahmini
  → Hastalık riski skorlama
```

#### Destek Vektör Makineleri (SVM)

```
Çalışma Prensibi:
  - Veri noktalarını ayıran en iyi hiper-düzlemi bulur
  - Kernel trick ile doğrusal olmayan sınırlar oluşturabilir
  - Destek vektörleri: sınıra en yakın noktalar

Kernel Seçenekleri:
  - RBF (Radial Basis Function): Genel amaçlı
  - Linear: Doğrusal ayrılabilir veriler
  - Polynomial: Polinom ilişkiler

Tarımsal Kullanım:
  → Toprak sınıflandırması (verimli/verimsiz)
  → Hastalık tespiti (hasta/sağlıklı)
```

#### K-En Yakın Komşu (KNN)

```
Çalışma Prensibi:
  1. Yeni veri noktasına en yakın K komşuyu bul
  2. Komşuların etiketlerine göre karar ver
     - Sınıflandırma: çoğunluk oylaması
     - Regresyon: komşuların ortalaması

Parametre Seçimi:
  - K değeri: Çok küçük → overfitting, çok büyük → underfitting
  - Uzaklık metriği: Öklid, Manhattan, Minkowski

Tarımsal Kullanım:
  → Benzer tarla koşullarına göre öneri
  → Bölge bazlı sınıflandırma
```

### 3.2 Gözetimsiz Öğrenme (Unsupervised Learning)

#### K-Means Kümeleme

```
Algoritma Adımları:
  1. K adet rastgele merkez noktası belirle
  2. Her veri noktasını en yakın merkeze ata
  3. Merkezleri yeniden hesapla
  4. Değişim olmayana kadar 2-3 adımlarını tekrarla

Optimal K Seçimi:
  - Elbow (Dirsek) Yöntemi: Inertia'nın keskin düştüğü nokta
  - Silhouette Skoru: Küme kalitesi ölçümü

Tarımsal Kullanım:
  → Benzer toprak özelliklerine sahip bölgeleri gruplama
  → Sulama ihtiyacına göre alan sınıflandırma
```

#### DBSCAN Kümeleme

```
Çalışma Prensibi:
  - Yoğunluk bazlı kümeleme algoritması
  - Küme sayısını önceden bilmeye gerek yoktur
  - Gürültü noktalarını otomatik tespit eder

Parametreler:
  - eps: Komşuluk yarıçapı
  - min_samples: Minimum komşu sayısı

Tarımsal Kullanım:
  → Coğrafi bölge kümeleme
  → Sensör ağı anomali bölgeleri tespiti
```

### 3.3 Model Değerlendirme Metrikleri

| Metrik | Görev | Formül/Açıklama |
|--------|-------|----------------|
| **RMSE** | Regresyon | √(Σ(gerçek - tahmin)² / n) |
| **MAE** | Regresyon | Σ|gerçek - tahmin| / n |
| **R²** | Regresyon | 1 - (SS_res / SS_tot) |
| **Accuracy** | Sınıflandırma | Doğru tahmin / Toplam |
| **F1-Score** | Sınıflandırma | 2 × (Precision × Recall) / (Precision + Recall) |
| **Çapraz Doğrulama** | Genel | K-fold ile model kararlılığı testi |

---

## 4. Zaman Serisi Analiz Yöntemleri

### 4.1 Durağanlık Testi (Augmented Dickey-Fuller)

```
H₀: Seri durağan değildir (birim kök vardır)
H₁: Seri durağandır

Karar: p-değeri < 0.05 ise H₀ reddedilir → Seri durağandır

Önem: ARIMA gibi modeller durağan seri gerektirir.
      Durağan olmayan serilere fark alma (differencing) uygulanır.
```

### 4.2 ARIMA (AutoRegressive Integrated Moving Average)

```
ARIMA(p, d, q) Bileşenleri:

  AR(p) - Otoregresif: y_t = c + φ₁y_{t-1} + φ₂y_{t-2} + ... + φ_py_{t-p}
    → Geçmiş değerlerin etkisi

  I(d) - Entegrasyon: d kez fark alma
    → Seriyi durağan hale getirir

  MA(q) - Hareketli Ortalama: y_t = μ + θ₁ε_{t-1} + θ₂ε_{t-2} + ... + θ_qε_{t-q}
    → Geçmiş tahmin hatalarının etkisi

Parametre Seçimi:
  - p: PACF grafiğinden belirlenir
  - d: ADF testi ile belirlenir
  - q: ACF grafiğinden belirlenir
  - AIC/BIC: Model karşılaştırma kriterleri

Tarımsal Kullanım:
  → Gelecek günlerin sıcaklık tahmini
  → Toprak nemi değişim tahmini
  → Yağış miktarı öngörüsü
```

### 4.3 Holt-Winters Üstel Düzeltme

```
Üç bileşenli model:
  - Seviye (Level): l_t = α × y_t + (1-α) × (l_{t-1} + b_{t-1})
  - Trend: b_t = β × (l_t - l_{t-1}) + (1-β) × b_{t-1}
  - Mevsimsellik: s_t = γ × (y_t - l_t) + (1-γ) × s_{t-m}

Düzeltme Parametreleri:
  - α (alpha): Seviye düzeltme (0-1)
  - β (beta): Trend düzeltme (0-1)
  - γ (gamma): Mevsimsel düzeltme (0-1)

Tarımsal Kullanım:
  → Mevsimsel sulama planlaması
  → Kısa vadeli hava durumu etkisi tahmini
```

### 4.4 Mevsimsel Ayrıştırma

```
Toplamsaal Model: Y_t = T_t + S_t + R_t
Çarpımsal Model: Y_t = T_t × S_t × R_t

Bileşenler:
  T_t: Trend bileşeni (uzun vadeli yön)
  S_t: Mevsimsel bileşen (periyodik tekrar)
  R_t: Artık (Residual) bileşen (rastgele gürültü)

Tarımsal Mevsimsellik Örnekleri:
  - Saatlik: Güneş ışığı döngüsü → 24 saat periyot
  - Haftalık: Sulama programı → 7 gün periyot
  - Yıllık: Mevsim değişimi → 365 gün periyot
```

---

## 5. Anomali Tespit Algoritmaları

### 5.1 Z-Score Yöntemi

```
Z = (x - μ) / σ

Eğer |Z| > 3 ise → Anomali

Avantaj: Basit, hızlı, yorumlaması kolay
Dezavantaj: Normal dağılım varsayımı gerektirir
```

### 5.2 Isolation Forest

```
Çalışma Prensibi:
  1. Rastgele bir özellik ve bölme noktası seç
  2. Veriyi ikiye böl
  3. Her nokta için ortalama izolasyon derinliğini hesapla
  4. Az derinlikte izole edilen noktalar → Anomali

Neden etkili?
  Anomaliler, normal veriden farklı olduğu için
  daha az bölme ile izole edilebilir.

Parametre: contamination (beklenen anomali oranı)
```

### 5.3 Local Outlier Factor (LOF)

```
Çalışma Prensibi:
  1. Her noktanın K-komşu yoğunluğunu hesapla
  2. Yoğunluğu komşularına göre düşük olan noktalar → Anomali

LOF Skoru:
  LOF ≈ 1 → Normal
  LOF >> 1 → Anomali

Avantaj: Yerel yoğunluk farkını yakalar
         (farklı yoğunluktaki bölgelerde çalışır)
```

### 5.4 Hareketli Ortalama Bazlı Tespit

```
Eşik = Hareketli_Ortalama ± k × Hareketli_Standart_Sapma

Eğer değer eşik dışındaysa → Anomali

Avantajları:
  ✓ Gerçek zamanlı uygulanabilir
  ✓ Mevsimsel değişikliklere uyum sağlar
  ✓ Düşük hesaplama maliyeti
  ✓ IoT cihazlarda edge computing'e uygun
```

---

## 6. Veri Görselleştirme Kütüphaneleri ve Teknikleri

### 6.1 Matplotlib (Statik Grafikler)

| Grafik Tipi | Kullanım Amacı | Tarımsal Uygulama |
|-------------|---------------|-------------------|
| **Çizgi Grafiği** | Zaman serisi trendi | Sıcaklık/nem değişimi |
| **Histogram** | Veri dağılımı | Sensör ölçüm dağılımı |
| **Scatter Plot** | İki değişken ilişkisi | Nem-sıcaklık ilişkisi |
| **Çoklu Alt Grafik** | Sensör karşılaştırma | Tüm sensörlerin eş zamanlı görünümü |

### 6.2 Seaborn (İstatistiksel Görselleştirme)

| Grafik Tipi | Kullanım Amacı | Tarımsal Uygulama |
|-------------|---------------|-------------------|
| **Isı Haritası** | Korelasyon matrisi | Sensörler arası ilişki haritası |
| **Kutu Grafiği (Box Plot)** | Dağılım + aykırı değer | Bölgesel veri karşılaştırma |
| **Violin Grafiği** | Dağılım şekli | Toprak kalitesi dağılımı |
| **Pair Plot** | Çoklu değişken ilişkisi | Tüm sensör çiftleri analizi |
| **KDE Plot** | Yoğunluk tahmini | Ölçüm yoğunluğu analizi |

### 6.3 Plotly (İnteraktif Web Grafikleri)

| Grafik Tipi | Özellikler | Tarımsal Uygulama |
|-------------|-----------|-------------------|
| **İnteraktif Zaman Serisi** | Zoom, pan, hover, range slider | Gerçek zamanlı sensör izleme |
| **Dashboard** | Çoklu senkronize grafik | Tarla durumu panosu |
| **Gauge (Gösterge)** | Anlık değer göstergesi | pH, nem, sıcaklık anlık durum |
| **Scatter Plot** | Trend çizgisi, renklendirme | Değişken ilişkisi analizi |
| **Anomali Grafiği** | Normal/anomali işaretleme | Sensör arızası tespiti |

### 6.4 Görselleştirme Teknikleri

```
1. Zaman Serisi Görselleştirme:
   - Hareketli ortalama overlay
   - Güven aralığı bandları
   - Anomali noktası işaretleme
   - Range slider ile tarih seçimi

2. İstatistiksel Görselleştirme:
   - Korelasyon ısı haritası (üçgen maske)
   - Box plot + notch (medyan güven aralığı)
   - KDE ile histogram overlay
   - Normal dağılım eğrisi karşılaştırma

3. Dashboard Teknikleri:
   - Real-time gauge göstergeleri
   - Çoklu sensör senkronize grafikleri
   - Renk kodlu uyarı sistemi
   - Otomatik yenileme (5 dakika)

4. Çıktı Formatları:
   - PNG/JPG: Rapor ve sunum için
   - HTML: Web dashboard'a gömme
   - Base64: Django template içine inline gömme
   - JSON: AJAX ile dinamik yükleme
```

---

## 7. Python ve Django Entegrasyonu

### 7.1 Django Proje Yapısına Entegrasyon

```python
# 1. settings.py'ye uygulama ekleme
INSTALLED_APPS = [
    ...
    'veri_analiz_modulu',
]

# 2. urls.py'ye URL ekleme
urlpatterns = [
    path('analiz/', include('veri_analiz_modulu.urls')),
]

# 3. Migration'ları çalıştırma
# python manage.py makemigrations veri_analiz_modulu
# python manage.py migrate
```

### 7.2 Django Model Yapısı

```
Sensor ──────────────── 1:N ──── SensorVerisi
  │                                    │
  │                                    │ (analiz edilir)
  │                                    ▼
  └── 1:N ──── AnalizSonucu ──── 1:N ──── SulamaOnerisi
```

### 7.3 API Endpoint'leri

| Endpoint | Metot | Açıklama |
|----------|-------|----------|
| `/analiz/` | GET | Ana dashboard |
| `/analiz/sensorler/` | GET | Sensör listesi |
| `/analiz/sensor/<id>/` | GET | Sensör detayı |
| `/analiz/api/sensor/<id>/veri/` | GET | Sensör verileri (JSON) |
| `/analiz/api/sensor/<id>/istatistik/` | GET | İstatistik sonuçları (JSON) |
| `/analiz/api/analiz/` | POST | Analiz çalıştır |
| `/analiz/api/korelasyon/` | GET | Korelasyon analizi |

### 7.4 Django Signal'ler ile Otomatik İzleme

```python
# Sensör verisi kaydedildiğinde otomatik tetiklenir:
# - Toprak nemi < 20% → Acil sulama önerisi oluştur
# - Toprak nemi < 35% → Yüksek öncelikli sulama önerisi
# - Sıcaklık ≤ 0°C → Don riski uyarısı
```

---

## 8. Kullanılan Kütüphaneler Özeti

| Kütüphane | Versiyon | Kullanım Alanı |
|-----------|----------|---------------|
| **Django** | ≥4.2 | Web framework, ORM, template engine |
| **NumPy** | ≥1.24 | Sayısal hesaplama, matris işlemleri |
| **Pandas** | ≥2.0 | Veri manipülasyonu, DataFrame |
| **SciPy** | ≥1.10 | İstatistiksel testler, korelasyon |
| **Scikit-learn** | ≥1.3 | ML algoritmaları, model değerlendirme |
| **Statsmodels** | ≥0.14 | ARIMA, Holt-Winters, ADF testi |
| **Matplotlib** | ≥3.7 | Statik grafikler (çizgi, histogram) |
| **Seaborn** | ≥0.12 | İstatistiksel görselleştirme |
| **Plotly** | ≥5.15 | İnteraktif web grafikleri, dashboard |
| **Joblib** | ≥1.3 | ML model kaydetme/yükleme |

---

> **Not:** Bu modül, Akıllı Tarım Yönetim Sistemi'nin veri analiz katmanını oluşturmaktadır.
> IoT sensörlerinden toplanan veriler bu modül aracılığıyla işlenir, analiz edilir ve
> görselleştirilir. Tüm kodlar Python 3.10+ ve Django 4.2+ ile uyumludur.
