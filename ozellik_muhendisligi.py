# -*- coding: utf-8 -*-
"""
+================================================================+
|         OZELLIK MUHENDISLIGI ARASTIRMA MODULU                  |
|         Akilli Tarim Yonetim Sistemi - AI/ML Modulu            |
|         Versiyon 1.0  |  Mayis 2025                            |
+================================================================+

Bu modul, tarimsal sensor verilerinden yeni ozellikler turetmek
ve en etkili ozellikleri secmek icin kullanilan tum teknikleri icerir.

ICINDEKILER:
    1. Ornek Veri Uretimi (demo amacli)
    2. Ozellik Muhendisligi Teknikleri
       2.1  Zaman Serisi Agregasyonu
       2.2  Polinomsal Ozellikler
       2.3  Fourier Donusumu
       2.4  Lag (Gecikme) Ozellikleri
       2.5  Hedef Kodlama
       2.6  Anomali Skoru
    3. Ozellik Secimi Yontemleri
       3.1  Korelasyon Analizi
       3.2  Mutual Information
       3.3  SHAP Degerleri
       3.4  Recursive Feature Elimination (RFE)
       3.5  Permutation Importance
    4. Tam Pipeline - Hepsini Bir Arada Calistirma
"""

# ============================================================
#  KONSOL KODLAMA AYARI (Windows uyumu)
# ============================================================
import sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

# ============================================================
#  GEREKLI KUTUPHANELERIN YUKLENMESI
# ============================================================
import numpy as np
import pandas as pd
import warnings

warnings.filterwarnings("ignore")

# Gorsellestirme (grafik cizdirmek istersen)
try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.rcParams["figure.figsize"] = (12, 5)
    matplotlib.rcParams["axes.grid"] = True
    GRAFIK_AKTIF = True
except ImportError:
    GRAFIK_AKTIF = False
    print("[!] matplotlib bulunamadi. Grafikler devre disi.")

# Makine öğrenmesi
try:
    from sklearn.ensemble import (
        RandomForestClassifier,
        IsolationForest,
        GradientBoostingClassifier,
    )
    from sklearn.feature_selection import (
        mutual_info_classif,
        RFE,
    )
    from sklearn.inspection import permutation_importance
    from sklearn.model_selection import cross_val_score, TimeSeriesSplit
    from sklearn.preprocessing import PolynomialFeatures, StandardScaler
    from sklearn.linear_model import LogisticRegression
    SKLEARN_AKTIF = True
except ImportError:
    SKLEARN_AKTIF = False
    print("⚠ scikit-learn bulunamadı. ML özellikleri devre dışı.")

# SHAP (model açıklanabilirliği)
try:
    import shap
    SHAP_AKTIF = True
except ImportError:
    SHAP_AKTIF = False
    print("⚠ shap bulunamadı. SHAP analizi devre dışı.")


# ============================================================
#  1. ÖRNEK VERİ ÜRETİMİ (Demo Amaçlı)
# ============================================================
def ornek_tarim_verisi_uret(gun_sayisi=365, rastgele_tohum=42):
    """
    Gerçekçi tarımsal sensör verisi üretir (demo amaçlı).

    Parametreler:
        gun_sayisi   : Kaç günlük veri üretileceği (varsayılan: 365)
        rastgele_tohum: Tekrarlanabilirlik için rastgele sayı tohumu

    Döndürür:
        pandas DataFrame — tarih indeksli sensör verileri
    """
    np.random.seed(rastgele_tohum)

    # ----- Tarih aralığı oluştur -----
    tarihler = pd.date_range(start="2024-01-01", periods=gun_sayisi, freq="D")

    # ----- Günler (0'dan başlayan sayaç, mevsimsellik için) -----
    gun = np.arange(gun_sayisi)

    # ----- Sıcaklık: mevsimsel sinüs eğrisi + gürültü -----
    #   Yaz ≈ 35°C, Kış ≈ 5°C civarı
    sicaklik = 20 + 15 * np.sin(2 * np.pi * gun / 365 - np.pi / 2) \
               + np.random.normal(0, 2, gun_sayisi)

    # ----- Nem: sıcaklıkla ters orantılı + gürültü -----
    nem = 70 - 0.8 * sicaklik + np.random.normal(0, 5, gun_sayisi)
    nem = np.clip(nem, 10, 100)  # %10 ile %100 arasında sınırla

    # ----- Toprak nemi: yağış ve buharlaşmaya bağlı -----
    toprak_nemi = 45 + 10 * np.sin(2 * np.pi * gun / 365) \
                  + np.random.normal(0, 4, gun_sayisi)
    toprak_nemi = np.clip(toprak_nemi, 5, 95)

    # ----- Yağış (mm): bazı günler yağmur, çoğu gün 0 -----
    yagis = np.where(
        np.random.random(gun_sayisi) < 0.25,         # %25 ihtimalle yağış
        np.random.exponential(8, gun_sayisi),         # üstel dağılım
        0
    )

    # ----- pH: hafif dalgalanma -----
    ph = 6.5 + 0.3 * np.sin(2 * np.pi * gun / 180) \
         + np.random.normal(0, 0.1, gun_sayisi)

    # ----- EC (Elektriksel İletkenlik, dS/m) -----
    ec = 1.2 + 0.3 * np.sin(2 * np.pi * gun / 90) \
         + np.random.normal(0, 0.1, gun_sayisi)

    # ----- NDVI (Bitki sağlığı indeksi, 0-1 arası) -----
    ndvi = 0.5 + 0.3 * np.sin(2 * np.pi * gun / 365 - np.pi / 3) \
           + np.random.normal(0, 0.03, gun_sayisi)
    ndvi = np.clip(ndvi, 0, 1)

    # ----- Mahsul türü (kategorik) -----
    mahsul_turleri = ["Buğday", "Mısır", "Domates", "Pamuk"]
    mahsul = np.random.choice(mahsul_turleri, gun_sayisi)

    # ----- Arazi parçası (kategorik) -----
    arazi_parcalari = ["Parsel-A", "Parsel-B", "Parsel-C"]
    arazi = np.random.choice(arazi_parcalari, gun_sayisi)

    # ----- Sulama kararı (hedef değişken): 1 = sula, 0 = sulama -----
    #   Toprak nemi düşükse ve sıcaklık yüksekse → sulama gerekli
    sulama_skoru = (50 - toprak_nemi) * 0.5 + (sicaklik - 20) * 0.3 - yagis * 0.2
    sulama_karari = (sulama_skoru > np.percentile(sulama_skoru, 55)).astype(int)

    # ----- DataFrame oluştur -----
    df = pd.DataFrame({
        "tarih":         tarihler,
        "sicaklik":      np.round(sicaklik, 1),
        "nem":           np.round(nem, 1),
        "toprak_nemi":   np.round(toprak_nemi, 1),
        "yagis_mm":      np.round(yagis, 1),
        "ph":            np.round(ph, 2),
        "ec":            np.round(ec, 2),
        "ndvi":          np.round(ndvi, 3),
        "mahsul_turu":   mahsul,
        "arazi_parcasi": arazi,
        "sulama_karari": sulama_karari,  # HEDEF DEĞİŞKEN
    })

    df = df.set_index("tarih")
    return df


# ============================================================
#  2. ÖZELLİK MÜHENDİSLİĞİ TEKNİKLERİ
# ============================================================

# ------------------------------------------------------------
#  2.1  ZAMAN SERİSİ AGREGASYONU
# ------------------------------------------------------------
def zaman_serisi_agregasyonu(df, sutunlar=None, pencereler=None):
    """
    Kayan pencere (rolling window) ile istatistiksel özellikler üretir.

    Ne yapar?
        Belirli bir sütun için son N günün ortalamasını, standart sapmasını,
        minimum ve maksimum değerlerini hesaplar.

    Neden önemli?
        Anlık değerler yerine trendleri yakalar.
        Örnek: "Son 7 gündeki ortalama toprak nemi" sulama kararı için
        çok daha bilgilendiricidir.

    ⚠ DİKKAT: Sadece GEÇMİŞ verilere bakılır (data leakage önlenir).
        min_periods=1 sayesinde ilk günlerde bile NaN oluşmaz.

    Parametreler:
        df        : Giriş DataFrame'i
        sutunlar  : Hangi sütunlara uygulanacak (varsayılan: sayısal sütunlar)
        pencereler: Pencere boyutları (varsayılan: [7, 14, 30] gün)

    Döndürür:
        Yeni özellikler eklenmiş DataFrame
    """
    df = df.copy()

    if sutunlar is None:
        sutunlar = ["sicaklik", "nem", "toprak_nemi", "yagis_mm"]

    if pencereler is None:
        pencereler = [7, 14, 30]

    for sutun in sutunlar:
        for pencere in pencereler:
            # --- Kayan Ortalama ---
            # Örnek: sicaklik_ort_7 = son 7 günün sıcaklık ortalaması
            df[f"{sutun}_ort_{pencere}"] = (
                df[sutun]
                .rolling(window=pencere, min_periods=1)
                .mean()
            )

            # --- Kayan Standart Sapma ---
            # Değişkenliği (volatiliteyi) ölçer
            df[f"{sutun}_std_{pencere}"] = (
                df[sutun]
                .rolling(window=pencere, min_periods=1)
                .std()
                .fillna(0)
            )

            # --- Kayan Minimum ---
            df[f"{sutun}_min_{pencere}"] = (
                df[sutun]
                .rolling(window=pencere, min_periods=1)
                .min()
            )

            # --- Kayan Maksimum ---
            df[f"{sutun}_max_{pencere}"] = (
                df[sutun]
                .rolling(window=pencere, min_periods=1)
                .max()
            )

    print(f"✅ Zaman serisi agregasyonu tamamlandı.")
    print(f"   → {len(sutunlar)} sütun × {len(pencereler)} pencere × 4 istatistik")
    print(f"   → {len(sutunlar) * len(pencereler) * 4} yeni özellik eklendi.")
    return df


# ------------------------------------------------------------
#  2.2  POLİNOMSAL ÖZELLİKLER
# ------------------------------------------------------------
def polinomsal_ozellikler(df, sutunlar=None, derece=2):
    """
    Sütunlar arasındaki etkileşimleri (çarpımları) hesaplar.

    Ne yapar?
        İki veya daha fazla sütunun çarpımını yeni özellik olarak ekler.
        Örnek: nem × sıcaklık = "sıcak ve nemli" durumunu yakalar.

    Neden önemli?
        Doğrusal modeller tek başına nem veya sıcaklığı göremez.
        Ama nem×sıcaklık etkileşimi hastalık riskini doğrudan gösterir.

    Parametreler:
        df       : Giriş DataFrame'i
        sutunlar : Hangi sütunlar arasında etkileşim üretilecek
        derece   : Polinom derecesi (2 = ikili çarpımlar, 3 = üçlü)

    Döndürür:
        Yeni özellikler eklenmiş DataFrame
    """
    df = df.copy()

    if sutunlar is None:
        sutunlar = ["sicaklik", "nem", "toprak_nemi"]

    # PolynomialFeatures: sklearn'ün etkileşim özellik üretici aracı
    #   interaction_only=True → sadece farklı sütunların çarpımı (a*b, a*c...)
    #   include_bias=False    → sabit terim (1) eklenmez
    poli = PolynomialFeatures(
        degree=derece,
        interaction_only=True,
        include_bias=False,
    )

    # Seçilen sütunları al, NaN varsa 0 ile doldur
    veri = df[sutunlar].fillna(0).values

    # Dönüşümü uygula
    poli_veri = poli.fit_transform(veri)

    # Yeni sütun isimleri oluştur
    poli_isimler = poli.get_feature_names_out(sutunlar)

    # Sadece etkileşim terimlerini ekle (orijinal sütunlar zaten var)
    for i, isim in enumerate(poli_isimler):
        if " " in isim:  # Etkileşim terimi (örn: "sicaklik nem")
            temiz_isim = isim.replace(" ", "_x_")
            df[f"poli_{temiz_isim}"] = poli_veri[:, i]

    yeni_ozellik_sayisi = sum(1 for isim in poli_isimler if " " in isim)
    print(f"✅ Polinomsal özellikler tamamlandı.")
    print(f"   → {yeni_ozellik_sayisi} etkileşim terimi eklendi (derece={derece}).")
    return df


# ------------------------------------------------------------
#  2.3  FOURIER DÖNÜŞÜMÜ (Mevsimsel Bileşenler)
# ------------------------------------------------------------
def fourier_ozellikleri(df, periyotlar=None):
    """
    Mevsimsel döngüleri sinüs ve kosinüs bileşenlerine ayırır.

    Ne yapar?
        Takvim gününü kullanarak farklı periyotlardaki döngüsel
        desenleri yakalar. Örneğin:
        - 7 gün  → haftalık döngü (sulama programı)
        - 30 gün → aylık döngü (hava durumu)
        - 365 gün → yıllık döngü (mevsimler)

    Neden önemli?
        Tarım doğası gereği döngüseldir. Mevsimsel desenleri sayısal
        olarak ifade etmek modelin "hangi mevsimde olduğumuzu"
        anlamasını sağlar.

    Matematiksel formül:
        sin_P = sin(2π × gün_numarası / P)
        cos_P = cos(2π × gün_numarası / P)

    Parametreler:
        df         : Giriş DataFrame'i (tarih indeksli olmalı)
        periyotlar : Döngü uzunlukları gün cinsinden

    Döndürür:
        Yeni Fourier özellikleri eklenmiş DataFrame
    """
    df = df.copy()

    if periyotlar is None:
        periyotlar = [7, 30, 365]

    # Tarih indeksinden gün numarasını al
    if isinstance(df.index, pd.DatetimeIndex):
        gun_numarasi = df.index.dayofyear
    else:
        gun_numarasi = np.arange(len(df))

    for periyot in periyotlar:
        # Sinüs bileşeni: döngünün "fazını" yakalar
        df[f"fourier_sin_{periyot}"] = np.sin(
            2 * np.pi * gun_numarasi / periyot
        ).round(4)

        # Kosinüs bileşeni: sinüse dik açılı tamamlayıcı
        df[f"fourier_cos_{periyot}"] = np.cos(
            2 * np.pi * gun_numarasi / periyot
        ).round(4)

    print(f"✅ Fourier özellikleri tamamlandı.")
    print(f"   → {len(periyotlar)} periyot × 2 (sin+cos) = {len(periyotlar)*2} yeni özellik.")
    return df


# ------------------------------------------------------------
#  2.4  LAG (GECİKME) ÖZELLİKLERİ
# ------------------------------------------------------------
def lag_ozellikleri(df, sutunlar=None, gecikmeler=None):
    """
    Geçmiş günlerin değerlerini yeni özellik olarak ekler.

    Ne yapar?
        Bir sütunun 1, 3, 7 veya 14 gün önceki değerini yeni bir
        sütun olarak ekler.
        Örnek: toprak_nemi_lag_7 = 7 gün önceki toprak nemi değeri

    Neden önemli?
        Geçmiş değerler geleceği tahmin etmek için çok güçlü sinyaller
        taşır. "Dün toprak nemi düşükse bugün sulama gerekir" gibi
        kuralları modelin öğrenmesini sağlar.

    Ayrıca: Değişim hızı (fark) da hesaplanır.
        Örnek: toprak_nemi_degisim_7 = bugünkü değer - 7 gün önceki değer
        Bu, trendin yönünü gösterir (artıyor mu, azalıyor mu?).

    Parametreler:
        df         : Giriş DataFrame'i
        sutunlar   : Hangi sütunlara uygulanacak
        gecikmeler : Kaç gün geriye bakılacak

    Döndürür:
        Lag ve değişim özellikleri eklenmiş DataFrame
    """
    df = df.copy()

    if sutunlar is None:
        sutunlar = ["sicaklik", "nem", "toprak_nemi", "ndvi"]

    if gecikmeler is None:
        gecikmeler = [1, 3, 7, 14]

    for sutun in sutunlar:
        for gecikme in gecikmeler:
            # --- Gecikmeli değer ---
            # shift(N) → sütunu N satır aşağı kaydırır (geçmişe bakar)
            df[f"{sutun}_lag_{gecikme}"] = df[sutun].shift(gecikme)

            # --- Değişim miktarı (fark) ---
            # Bugün - N gün önce = ne kadar değişmiş?
            df[f"{sutun}_degisim_{gecikme}"] = df[sutun] - df[sutun].shift(gecikme)

    # İlk satırlarda lag değeri olmayacağı için NaN oluşur → 0 ile doldur
    df = df.fillna(0)

    print(f"✅ Lag özellikleri tamamlandı.")
    print(f"   → {len(sutunlar)} sütun × {len(gecikmeler)} gecikme × 2 (lag+değişim)")
    print(f"   → {len(sutunlar) * len(gecikmeler) * 2} yeni özellik eklendi.")
    return df


# ------------------------------------------------------------
#  2.5  HEDEF KODLAMA (Target Encoding)
# ------------------------------------------------------------
def hedef_kodlama(df, kategorik_sutunlar=None, hedef_sutun="sulama_karari"):
    """
    Kategorik değişkenleri hedef değişkenin ortalamasıyla kodlar.

    Ne yapar?
        Her kategori için hedef değişkenin ortalamasını hesaplar ve
        kategori yerine bu sayısal değeri kullanır.
        Örnek: Mahsul türü "Domates" → sulama oranı 0.72
               Mahsul türü "Buğday"  → sulama oranı 0.35

    Neden önemli?
        One-hot encoding çok fazla sütun üretir.
        Hedef kodlama tek sütunda kategorinin hedefle ilişkisini yakalar.

    ⚠ DİKKAT: Overfitting riski!
        Bunu önlemek için smoothing (yumuşatma) uygulanır:
        kodlama = (n × kategori_ort + m × genel_ort) / (n + m)
        Burada n = kategorideki örnek sayısı, m = yumuşatma faktörü

    Parametreler:
        df                  : Giriş DataFrame'i
        kategorik_sutunlar  : Kodlanacak sütunlar
        hedef_sutun         : Hedef değişken adı

    Döndürür:
        Kodlanmış özellikler eklenmiş DataFrame
    """
    df = df.copy()

    if kategorik_sutunlar is None:
        kategorik_sutunlar = ["mahsul_turu", "arazi_parcasi"]

    genel_ortalama = df[hedef_sutun].mean()
    yumusatma = 10  # Küçük kategorilerde genel ortalamaya yaklaştırır

    for sutun in kategorik_sutunlar:
        # Her kategori için hedef ortalamasını hesapla
        istatistikler = df.groupby(sutun)[hedef_sutun].agg(["mean", "count"])

        # Yumuşatılmış kodlama: küçük gruplar genel ortalamaya çekilir
        kodlama = (
            (istatistikler["count"] * istatistikler["mean"]
             + yumusatma * genel_ortalama)
            / (istatistikler["count"] + yumusatma)
        )

        # Sözlük olarak eşle
        kodlama_sozluk = kodlama.to_dict()

        # Yeni sütun ekle
        df[f"{sutun}_hedef_kod"] = df[sutun].map(kodlama_sozluk).round(4)

        print(f"   📌 {sutun} kodlaması:")
        for kategori, deger in sorted(kodlama_sozluk.items()):
            print(f"      {kategori:15s} → {deger:.4f}")

    print(f"✅ Hedef kodlama tamamlandı ({len(kategorik_sutunlar)} sütun).")
    return df


# ------------------------------------------------------------
#  2.6  ANOMALİ SKORU (Isolation Forest)
# ------------------------------------------------------------
def anomali_skoru(df, sutunlar=None, kontaminasyon=0.05):
    """
    Sensör verilerindeki anormal okumaları tespit eder ve skorlar.

    Ne yapar?
        Isolation Forest algoritması kullanarak her veri noktasının
        ne kadar "normal dışı" olduğunu -1 ile 0 arasında skorlar.
        -1'e yakın = çok anormal, 0'a yakın = normal

    Neden önemli?
        Sensörler arızalanabilir veya aşırı hava olayları yaşanabilir.
        Anomali skorları modelin bu durumları tanımasını sağlar.
        Ayrıca hastalık belirtileri genellikle normal dışı okumalarda
        gizlidir.

    Isolation Forest nasıl çalışır?
        1. Rastgele bir özellik seçer
        2. O özellik için rastgele bir bölme noktası seçer
        3. Veriyi ikiye ayırır
        4. Bunu tekrarlar (ağaç oluşturur)
        5. Anomaliler daha az bölme ile izole edilir (ağaçta yukarıda kalır)

    Parametreler:
        df              : Giriş DataFrame'i
        sutunlar        : Anomali tespiti yapılacak sütunlar
        kontaminasyon   : Beklenen anomali oranı (varsayılan: %5)

    Döndürür:
        Anomali skoru ve etiketi eklenmiş DataFrame
    """
    if not SKLEARN_AKTIF:
        print("⚠ scikit-learn gerekli. Anomali skoru atlandı.")
        return df

    df = df.copy()

    if sutunlar is None:
        sutunlar = ["sicaklik", "nem", "toprak_nemi", "ph", "ec"]

    # Sadece sayısal sütunları al
    veri = df[sutunlar].fillna(0).values

    # Isolation Forest modelini oluştur ve eğit
    model = IsolationForest(
        contamination=kontaminasyon,  # Verinin %5'i anomali bekleniyor
        random_state=42,
        n_estimators=100,             # 100 ağaç kullan
    )
    model.fit(veri)

    # Anomali skoru: negatif = anomali, pozitif = normal
    skorlar = model.decision_function(veri)

    # 0-1 aralığına normalize et (1 = en anormal)
    skor_min = skorlar.min()
    skor_max = skorlar.max()
    df["anomali_skoru"] = (
        (skor_max - skorlar) / (skor_max - skor_min)
    ).round(4)

    # Anomali etiketi: -1 = anomali, 1 = normal
    df["anomali_etiketi"] = model.predict(veri)

    anomali_sayisi = (df["anomali_etiketi"] == -1).sum()
    print(f"✅ Anomali skoru tamamlandı.")
    print(f"   → {anomali_sayisi} anomali tespit edildi ({anomali_sayisi/len(df)*100:.1f}%).")
    return df


# ============================================================
#  3. ÖZELLİK SEÇİMİ YÖNTEMLERİ
# ============================================================

def sayisal_sutunlari_al(df, hedef_sutun="sulama_karari"):
    """Hedef ve kategorik sütunları hariç tutarak sayısal sütunları döndürür."""
    haric = [hedef_sutun, "mahsul_turu", "arazi_parcasi"]
    sayisal = df.select_dtypes(include=[np.number]).columns.tolist()
    return [s for s in sayisal if s not in haric]


# ------------------------------------------------------------
#  3.1  KORELASYON ANALİZİ
# ------------------------------------------------------------
def korelasyon_analizi(df, esik=0.95, hedef_sutun="sulama_karari"):
    """
    Birbirine çok benzeyen (yüksek korelasyonlu) özellikleri tespit eder.

    Ne yapar?
        Tüm özellik çiftlerinin Pearson korelasyonunu hesaplar.
        |r| > 0.95 olan çiftlerden birini "gereksiz" olarak işaretler.

    Neden önemli?
        İki sütun aynı bilgiyi taşıyorsa birini silmek:
        - Modeli hızlandırır
        - Overfitting riskini azaltır
        - Yorumlanabilirliği artırır

    Parametreler:
        df          : Giriş DataFrame'i
        esik        : Korelasyon eşiği (varsayılan: 0.95)
        hedef_sutun : Hedef değişken adı

    Döndürür:
        (kaldırılacak sütunlar listesi, korelasyon matrisi)
    """
    ozellikler = sayisal_sutunlari_al(df, hedef_sutun)
    korelasyon = df[ozellikler].corr().abs()

    # Üst üçgen matris (aynı çifti iki kez saymamak için)
    ust_ucgen = np.triu(np.ones(korelasyon.shape), k=1).astype(bool)

    kaldirilacaklar = set()
    yuksek_korelasyonlar = []

    for i in range(len(korelasyon.columns)):
        for j in range(i + 1, len(korelasyon.columns)):
            if korelasyon.iloc[i, j] > esik:
                sutun_i = korelasyon.columns[i]
                sutun_j = korelasyon.columns[j]
                yuksek_korelasyonlar.append(
                    (sutun_i, sutun_j, korelasyon.iloc[i, j])
                )
                # İkincisini kaldır (ilkini tut)
                kaldirilacaklar.add(sutun_j)

    print(f"✅ Korelasyon analizi tamamlandı (eşik: {esik}).")
    print(f"   → {len(yuksek_korelasyonlar)} yüksek korelasyonlu çift bulundu.")
    print(f"   → {len(kaldirilacaklar)} sütun kaldırılmaya aday.")

    if yuksek_korelasyonlar:
        print(f"\n   En yüksek korelasyonlu 5 çift:")
        for s1, s2, r in sorted(yuksek_korelasyonlar, key=lambda x: -x[2])[:5]:
            print(f"      {s1:30s} ↔ {s2:30s}  r={r:.4f}")

    return list(kaldirilacaklar), korelasyon


# ------------------------------------------------------------
#  3.2  MUTUAL INFORMATION (Karşılıklı Bilgi)
# ------------------------------------------------------------
def mutual_information_secimi(df, hedef_sutun="sulama_karari", ust_n=20):
    """
    Her özelliğin hedef değişkenle paylaştığı bilgi miktarını ölçer.

    Ne yapar?
        Mutual Information (MI), iki değişken arasındaki bağımlılığı ölçer.
        MI = 0 → bağımsız (özellik işe yaramaz)
        MI > 0 → bağımlılık var (özellik bilgi taşıyor)

    Neden önemli?
        Korelasyondan farklı olarak doğrusal olmayan ilişkileri de yakalar.
        Örnek: Sıcaklık ve sulama kararı arasında U-şeklinde bir ilişki
        varsa korelasyon bunu göremez ama MI yakalar.

    Parametreler:
        df          : Giriş DataFrame'i
        hedef_sutun : Hedef değişken
        ust_n       : Kaç özellik gösterilecek (varsayılan: 20)

    Döndürür:
        Önem sıralaması (pandas Series)
    """
    if not SKLEARN_AKTIF:
        print("⚠ scikit-learn gerekli.")
        return None

    ozellikler = sayisal_sutunlari_al(df, hedef_sutun)
    X = df[ozellikler].fillna(0)
    y = df[hedef_sutun]

    # MI skorlarını hesapla
    mi_skorlari = mutual_info_classif(X, y, random_state=42)

    # Sonuçları DataFrame'e dönüştür
    sonuclar = pd.Series(mi_skorlari, index=ozellikler).sort_values(ascending=False)

    print(f"✅ Mutual Information analizi tamamlandı.")
    print(f"\n   En bilgilendirici {min(ust_n, len(sonuclar))} özellik:")
    for ozellik, skor in sonuclar.head(ust_n).items():
        # Görsel çubuk
        cubuk = "█" * int(skor / sonuclar.max() * 20)
        print(f"      {ozellik:35s}  MI={skor:.4f}  {cubuk}")

    return sonuclar


# ------------------------------------------------------------
#  3.3  SHAP DEĞERLERİ
# ------------------------------------------------------------
def shap_analizi(df, hedef_sutun="sulama_karari", ust_n=20):
    """
    Her özelliğin model tahminlerine katkısını SHAP ile açıklar.

    Ne yapar?
        SHAP (SHapley Additive exPlanations), oyun teorisine dayalı bir
        yöntemdir. Her özelliğin tahmini ne kadar değiştirdiğini hesaplar.

    Neden önemli?
        - Model agnostik: her modelle çalışır
        - Hem yerel (tek tahmin) hem küresel (tüm veri) açıklama sağlar
        - İşaret bilgisi verir: özellik tahmini artırıyor mu, azaltıyor mu?

    Parametreler:
        df          : Giriş DataFrame'i
        hedef_sutun : Hedef değişken
        ust_n       : Kaç özellik gösterilecek

    Döndürür:
        Önem sıralaması (pandas Series)
    """
    if not SHAP_AKTIF or not SKLEARN_AKTIF:
        print("⚠ shap ve scikit-learn kütüphaneleri gerekli.")
        return None

    ozellikler = sayisal_sutunlari_al(df, hedef_sutun)
    X = df[ozellikler].fillna(0)
    y = df[hedef_sutun]

    # Gradient Boosting modeli eğit (SHAP ile iyi çalışır)
    model = GradientBoostingClassifier(
        n_estimators=100, max_depth=4, random_state=42
    )
    model.fit(X, y)

    # SHAP açıklayıcısı oluştur
    aciklayici = shap.TreeExplainer(model)
    shap_degerleri = aciklayici.shap_values(X)

    # Küresel önem: her özellik için ortalama |SHAP|
    if isinstance(shap_degerleri, list):
        shap_degerleri = shap_degerleri[1]  # Pozitif sınıf

    onem = np.abs(shap_degerleri).mean(axis=0)
    sonuclar = pd.Series(onem, index=ozellikler).sort_values(ascending=False)

    print(f"✅ SHAP analizi tamamlandı.")
    print(f"\n   En etkili {min(ust_n, len(sonuclar))} özellik (ortalama |SHAP|):")
    for ozellik, skor in sonuclar.head(ust_n).items():
        cubuk = "█" * int(skor / sonuclar.max() * 20)
        print(f"      {ozellik:35s}  SHAP={skor:.4f}  {cubuk}")

    return sonuclar


# ------------------------------------------------------------
#  3.4  RECURSIVE FEATURE ELIMINATION (RFE)
# ------------------------------------------------------------
def rfe_secimi(df, hedef_sutun="sulama_karari", hedef_ozellik_sayisi=15):
    """
    Zayıf özellikleri adım adım atarak en iyi alt kümeyi bulur.

    Ne yapar?
        1. Tüm özelliklerle model eğitir
        2. En zayıf özelliği bulur ve çıkarır
        3. Tekrar model eğitir
        4. İstenen sayıya ulaşana kadar tekrarlar

    Neden önemli?
        Özellikler arası etkileşimleri dikkate alır.
        Tek başına zayıf ama birlikte güçlü olan özellikleri korur.

    Parametreler:
        df                     : Giriş DataFrame'i
        hedef_sutun            : Hedef değişken
        hedef_ozellik_sayisi   : Kaç özellik kalacak (varsayılan: 15)

    Döndürür:
        (seçilen özellikler listesi, sıralama)
    """
    if not SKLEARN_AKTIF:
        print("⚠ scikit-learn gerekli.")
        return None, None

    ozellikler = sayisal_sutunlari_al(df, hedef_sutun)
    X = df[ozellikler].fillna(0)
    y = df[hedef_sutun]

    # Veriyi ölçeklendir (Lojistik Regresyon için gerekli)
    olcekleyici = StandardScaler()
    X_olcekli = olcekleyici.fit_transform(X)

    # Lojistik Regresyon ile RFE
    model = LogisticRegression(max_iter=1000, random_state=42)
    rfe = RFE(
        estimator=model,
        n_features_to_select=min(hedef_ozellik_sayisi, len(ozellikler)),
        step=1,  # Her adımda 1 özellik çıkar
    )
    rfe.fit(X_olcekli, y)

    # Sonuçları topla
    secilen = [ozellikler[i] for i in range(len(ozellikler)) if rfe.support_[i]]
    siralama = pd.Series(rfe.ranking_, index=ozellikler).sort_values()

    print(f"✅ RFE tamamlandı.")
    print(f"   → {len(ozellikler)} özellikten {len(secilen)} tanesi seçildi.\n")
    print(f"   Seçilen özellikler:")
    for i, ozellik in enumerate(secilen, 1):
        print(f"      {i:2d}. {ozellik}")

    return secilen, siralama


# ------------------------------------------------------------
#  3.5  PERMUTATION IMPORTANCE
# ------------------------------------------------------------
def permutasyon_onemi(df, hedef_sutun="sulama_karari", ust_n=20):
    """
    Her özelliğin değerleri karıştırıldığında model kaybının artışını ölçer.

    Ne yapar?
        1. Normal modelde performansı ölç
        2. Bir özelliğin değerlerini rastgele karıştır
        3. Performans düşüşünü ölç
        4. Düşüş büyükse → o özellik önemli

    Neden önemli?
        - Model agnostik (her modelle çalışır)
        - Gerçek model performansına dayalı
        - Overfitting'den etkilenmez

    Parametreler:
        df          : Giriş DataFrame'i
        hedef_sutun : Hedef değişken
        ust_n       : Kaç özellik gösterilecek

    Döndürür:
        Önem sıralaması (pandas Series)
    """
    if not SKLEARN_AKTIF:
        print("⚠ scikit-learn gerekli.")
        return None

    ozellikler = sayisal_sutunlari_al(df, hedef_sutun)
    X = df[ozellikler].fillna(0)
    y = df[hedef_sutun]

    # Random Forest modeli eğit
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)

    # Permutation importance hesapla
    sonuc = permutation_importance(
        model, X, y,
        n_repeats=10,      # Her özellik 10 kez karıştırılır
        random_state=42,
    )

    onem = pd.Series(
        sonuc.importances_mean, index=ozellikler
    ).sort_values(ascending=False)

    print(f"✅ Permutation Importance tamamlandı.")
    print(f"\n   En önemli {min(ust_n, len(onem))} özellik:")
    for ozellik, skor in onem.head(ust_n).items():
        if skor > 0:
            cubuk = "█" * int(skor / max(onem.max(), 0.001) * 20)
            print(f"      {ozellik:35s}  Önem={skor:.4f}  {cubuk}")

    return onem


# ============================================================
#  4. TAM PİPELINE — HEPSİNİ BİR ARADA ÇALIŞTIRMA
# ============================================================
def tam_pipeline():
    """
    Tüm özellik mühendisliği ve seçimi adımlarını sırasıyla çalıştırır.

    Akış:
        Veri Üretimi → Özellik Mühendisliği → Özellik Seçimi → Sonuç Raporu
    """
    print("=" * 65)
    print("  AKILLI TARIM YÖNETİM SİSTEMİ")
    print("  Özellik Mühendisliği Pipeline'ı")
    print("=" * 65)

    # ── ADIM 1: Veri Üretimi ──
    print("\n📊 ADIM 1: Örnek veri üretiliyor...")
    df = ornek_tarim_verisi_uret(gun_sayisi=365)
    print(f"   → {df.shape[0]} satır, {df.shape[1]} sütun üretildi.")
    print(f"   → Sütunlar: {', '.join(df.columns.tolist())}")

    # ── ADIM 2: Özellik Mühendisliği ──
    print("\n" + "─" * 65)
    print("🔧 ADIM 2: Özellik mühendisliği uygulanıyor...\n")

    # 2.1 Zaman serisi agregasyonu
    print("── 2.1 Zaman Serisi Agregasyonu ──")
    df = zaman_serisi_agregasyonu(df)

    # 2.2 Polinomsal özellikler
    print("\n── 2.2 Polinomsal Özellikler ──")
    df = polinomsal_ozellikler(df)

    # 2.3 Fourier özellikleri
    print("\n── 2.3 Fourier Dönüşümü ──")
    df = fourier_ozellikleri(df)

    # 2.4 Lag özellikleri
    print("\n── 2.4 Lag (Gecikme) Özellikleri ──")
    df = lag_ozellikleri(df)

    # 2.5 Hedef kodlama
    print("\n── 2.5 Hedef Kodlama ──")
    df = hedef_kodlama(df)

    # 2.6 Anomali skoru
    print("\n── 2.6 Anomali Skoru ──")
    df = anomali_skoru(df)

    print(f"\n📈 Özellik mühendisliği sonrası: {df.shape[1]} sütun (başlangıç: 10)")

    # ── ADIM 3: Özellik Seçimi ──
    print("\n" + "─" * 65)
    print("🎯 ADIM 3: Özellik seçimi uygulanıyor...\n")

    # 3.1 Korelasyon filtresi
    print("── 3.1 Korelasyon Analizi ──")
    kaldirilacaklar, _ = korelasyon_analizi(df, esik=0.95)

    # Yüksek korelasyonlu sütunları kaldır
    if kaldirilacaklar:
        df_temiz = df.drop(columns=kaldirilacaklar, errors="ignore")
        print(f"   → {len(kaldirilacaklar)} sütun kaldırıldı.")
    else:
        df_temiz = df.copy()

    # 3.2 Mutual Information
    print("\n── 3.2 Mutual Information ──")
    mi_sonuc = mutual_information_secimi(df_temiz, ust_n=10)

    # 3.3 Permutation Importance
    print("\n── 3.3 Permutation Importance ──")
    pi_sonuc = permutasyon_onemi(df_temiz, ust_n=10)

    # 3.4 RFE
    print("\n── 3.4 Recursive Feature Elimination ──")
    secilen_ozellikler, _ = rfe_secimi(df_temiz, hedef_ozellik_sayisi=15)

    # 3.5 SHAP (opsiyonel)
    if SHAP_AKTIF:
        print("\n── 3.5 SHAP Analizi ──")
        shap_sonuc = shap_analizi(df_temiz, ust_n=10)

    # ── ADIM 4: Model Karşılaştırması ──
    print("\n" + "─" * 65)
    print("🏆 ADIM 4: Model performans karşılaştırması\n")

    if SKLEARN_AKTIF and secilen_ozellikler:
        orijinal_ozellikler = ["sicaklik", "nem", "toprak_nemi",
                                "yagis_mm", "ph", "ec", "ndvi"]

        # Orijinal özelliklerle model
        X_orijinal = df[orijinal_ozellikler].fillna(0)
        y = df["sulama_karari"]
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        cv = TimeSeriesSplit(n_splits=5)
        skor_orijinal = cross_val_score(model, X_orijinal, y, cv=cv, scoring="f1")

        # Mühendislik yapılmış özelliklerle model
        X_yeni = df_temiz[secilen_ozellikler].fillna(0)
        skor_yeni = cross_val_score(model, X_yeni, y, cv=cv, scoring="f1")

        print(f"   Orijinal özelliklerle F1 :  {skor_orijinal.mean():.4f} "
              f"(±{skor_orijinal.std():.4f})")
        print(f"   Mühendislik sonrası F1   :  {skor_yeni.mean():.4f} "
              f"(±{skor_yeni.std():.4f})")

        iyilesme = (skor_yeni.mean() - skor_orijinal.mean()) / skor_orijinal.mean() * 100
        print(f"\n   {'📈' if iyilesme > 0 else '📉'} İyileşme: %{iyilesme:+.1f}")

    # ── ÖZET ──
    print("\n" + "=" * 65)
    print("  📋 ÖZET RAPOR")
    print("=" * 65)
    print(f"  Başlangıç özellik sayısı  :  10")
    print(f"  Üretilen özellik sayısı   :  {df.shape[1]}")
    print(f"  Korelasyon filtresi sonrası:  {df_temiz.shape[1]}")
    if secilen_ozellikler:
        print(f"  RFE ile seçilen           :  {len(secilen_ozellikler)}")
    print("=" * 65)

    return df_temiz


# ============================================================
#  PROGRAMI ÇALIŞTIR
# ============================================================
if __name__ == "__main__":
    sonuc_df = tam_pipeline()
