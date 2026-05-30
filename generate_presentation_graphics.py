import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns

# Dizin Kurulumu
output_dir = os.path.join("media", "presentation")
os.makedirs(output_dir, exist_ok=True)

# Renk Paleti (Tasarım Standartlarına Uygun)
COLORS = {
    'primary': '#2C3E6B',  # Lacivert
    'accent': '#1A7A4A',   # Yeşil
    'warning': '#D97706',  # Turuncu
    'error': '#DC2626',    # Kırmızı
    'light_bg': '#F8FAFC', # Açık Arka Plan
    'gray': '#64748B',      # Gri
    'light_gray': '#E2E8F0' # Açık Gri
}

# Matplotlib global stil ayarları
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['text.color'] = COLORS['primary']
plt.rcParams['axes.labelcolor'] = COLORS['primary']
plt.rcParams['xtick.color'] = COLORS['primary']
plt.rcParams['ytick.color'] = COLORS['primary']


# =============================================================================
# 1. SİSTEM MİMARİSİ AKIŞ DİYAGRAMI (Slayt 3)
# =============================================================================
def draw_system_architecture():
    fig, ax = plt.subplots(figsize=(16, 9), dpi=120)
    ax.set_facecolor(COLORS['light_bg'])
    fig.patch.set_facecolor(COLORS['light_bg'])
    
    # Eksen sınırlarını ayarla ve kapat
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    plt.axis('off')
    
    # Başlık
    ax.text(8, 8.2, "AKILLI TARIM YÖNETİM SİSTEMİ - TEKNİK MİMARİ AKIŞI", 
            fontsize=24, fontweight='bold', color=COLORS['primary'], ha='center')
    
    # Slayt Alt Bilgisi
    ax.text(8, 0.5, "Slayt 3 | Sistem Mimarisi ve Veri Entegrasyonu", 
            fontsize=12, style='italic', color=COLORS['gray'], ha='center')
    
    # Blok kutularının koordinatları ve isimleri
    blocks = [
        # (x, y, genişlik, yükseklik, başlık, detay, renk)
        (1.0, 3.5, 2.0, 1.8, "Sensör (IoT)\nGateway", "Sıcaklık, Nem,\nToprak Nemi\n(MicroPython)", COLORS['accent']),
        (3.8, 3.5, 2.0, 1.8, "MQTT Broker\n(Mosquitto)", "Veri Taşıma\n(TLS, Port 8883)\n2.0 QoS 1", COLORS['primary']),
        (6.6, 3.5, 2.0, 1.8, "Django Backend\n(Celery/Channels)", "Asenkron Kuyruk\n& WebSocket\nREST Gateway", COLORS['primary']),
        (9.4, 3.5, 2.0, 1.8, "FastAPI\nML Servisi", "Pydantic v2\nTahmin API\n(SLA <150ms)", COLORS['primary']),
        (12.8, 5.0, 2.2, 1.6, "TimescaleDB\n(Veritabanı)", "Zaman Serisi\nHypertables\n& Aggregations", COLORS['warning']),
        (12.8, 2.0, 2.2, 1.6, "Yönetim Paneli\n& Mobil Uygulama", "Canlı İzleme\nGrafik Raporlama\nSulama Kontrolü", COLORS['accent'])
    ]
    
    # Blokları Çiz
    for x, y, w, h, title, detail, color in blocks:
        # Kutuyu çiz (rounded corners)
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1", 
                                      linewidth=2, edgecolor=color, facecolor='white', zorder=2)
        ax.add_patch(rect)
        
        # Üst şerit boyama (Renkli başlık alanı)
        header_rect = patches.FancyBboxPatch((x, y+h-0.45), w, 0.45, boxstyle="round,pad=0.1", 
                                             linewidth=0, facecolor=color, zorder=3)
        ax.add_patch(header_rect)
        
        # Başlık Metni
        ax.text(x + w/2, y + h - 0.25, title, fontsize=12, fontweight='bold', 
                color='white', ha='center', va='center', zorder=4)
        
        # Detay Metni
        ax.text(x + w/2, y + (h-0.4)/2, detail, fontsize=9, color=COLORS['gray'], 
                ha='center', va='center', zorder=4)
        
    # Okları Çiz
    arrows = [
        # (x, y, dx, dy, label)
        (3.1, 4.4, 0.6, 0.0, "WiFi/4G\nMQTT"),
        (5.9, 4.4, 0.6, 0.0, "WS/TCP"),
        (8.7, 4.4, 0.6, 0.0, "REST\nBridge"),
        (11.5, 4.4, 1.2, 1.0, "Bulk Write\npsycopg2"),
        (11.5, 4.4, 1.2, -1.0, "Tahmin/SLA\nJSON")
    ]
    
    for x, y, dx, dy, label in arrows:
        ax.arrow(x, y, dx, dy, head_width=0.18, head_length=0.18, fc=COLORS['gray'], ec=COLORS['gray'], zorder=1)
        # Ok üzerine metin ekle
        ax.text(x + dx/2, y + dy/2 + 0.2, label, fontsize=8, color=COLORS['gray'], ha='center', va='center')
        
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "sistem_mimarisi.png"), bbox_inches='tight', facecolor=COLORS['light_bg'])
    plt.close()
    print("Mimari Diyagram Kaydedildi.")


# =============================================================================
# 2. 7 GÜNLÜK SENSÖR TRENDİ ÇİZGİ GRAFİĞİ (Slayt 4)
# =============================================================================
def draw_sensor_trends():
    fig, ax = plt.subplots(figsize=(16, 9), dpi=120)
    ax.set_facecolor('white')
    fig.patch.set_facecolor(COLORS['light_bg'])
    
    # Mock Zaman Serisi Verisi
    dates = pd.date_range(start="2026-05-24", periods=7, freq='D')
    date_labels = [d.strftime('%d %b') for d in dates]
    
    # Sensör okumaları simülasyonu
    toprak_nemi = [42.1, 38.5, 33.2, 28.1, 24.5, 58.4, 52.1] # 6. gün sulama yapılmış
    hava_sicakligi = [28.4, 30.1, 33.5, 34.2, 35.8, 27.5, 29.2]
    hava_nemi = [55.2, 51.0, 47.4, 42.1, 38.0, 68.2, 60.5]
    
    # Çizgileri çiz
    ax.plot(date_labels, toprak_nemi, marker='o', linewidth=3, color=COLORS['accent'], label="Toprak Nemi (%)")
    ax.plot(date_labels, hava_sicakligi, marker='s', linewidth=3, color=COLORS['warning'], label="Hava Sıcaklığı (°C)")
    ax.plot(date_labels, hava_nemi, marker='^', linewidth=3, color=COLORS['primary'], label="Hava Nemi (%)")
    
    # Sulama gününü işaretle
    ax.axvline(x=5, color=COLORS['error'], linestyle='--', linewidth=2)
    ax.text(5.1, 65, "Otomatik Sulama Tetiklendi\n(Toprak Nemi < %25)", color=COLORS['error'], fontsize=11, fontweight='bold')
    
    # Grafik Süslemesi
    ax.set_title("7 GÜNLÜK SENSÖR VERİLERİ VE SULAMA TETİKLEME ANALİZİ", fontsize=20, fontweight='bold', pad=20)
    ax.set_xlabel("Tarih", fontsize=14, labelpad=10)
    ax.set_ylabel("Ölçüm Değeri", fontsize=14, labelpad=10)
    ax.grid(True, linestyle=':', alpha=0.6, color=COLORS['gray'])
    ax.legend(fontsize=12, loc='upper left')
    ax.set_ylim(0, 80)
    
    # Alt Bilgi
    plt.figtext(0.5, 0.02, "Slayt 4 | IoT Sensör Gerçek Zamanlı İzleme Trendleri", 
                fontsize=12, style='italic', color=COLORS['gray'], ha='center')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "sensor_trendleri.png"), bbox_inches='tight', facecolor=COLORS['light_bg'])
    plt.close()
    print("Sensör Trend Grafiği Kaydedildi.")


# =============================================================================
# 3. ÖZELLİK KORELASYON ISI HARİTASI (Slayt 4)
# =============================================================================
def draw_correlation_matrix():
    fig, ax = plt.subplots(figsize=(16, 9), dpi=120)
    fig.patch.set_facecolor(COLORS['light_bg'])
    
    # Mock Korelasyon Matrisi Verisi
    features = ['Toprak Nemi', 'Hava Sıcaklığı', 'Hava Nemi', 'Rüzgar Hızı', 'Yağış Miktarı', 'Su Tüketimi']
    data = {
        'Toprak Nemi':      [ 1.00, -0.45,  0.55, -0.12,  0.68, -0.72],
        'Hava Sıcaklığı':   [-0.45,  1.00, -0.68,  0.32, -0.22,  0.81],
        'Hava Nemi':        [ 0.55, -0.68,  1.00, -0.25,  0.41, -0.58],
        'Rüzgar Hızı':      [-0.12,  0.32, -0.25,  1.00, -0.05,  0.28],
        'Yağış Miktarı':    [ 0.68, -0.22,  0.41, -0.05,  1.00, -0.50],
        'Su Tüketimi':      [-0.72,  0.81, -0.58,  0.28, -0.50,  1.00]
    }
    df = pd.DataFrame(data, index=features)
    
    # Heatmap çiz
    sns.heatmap(df, annot=True, cmap="coolwarm", fmt=".2f", linewidths=1, square=True,
                cbar_kws={'label': 'Korelasyon Katsayısı'}, annot_kws={'size': 12, 'weight': 'bold'})
    
    ax.set_title("TARIMSAL ÖZELLİKLER KORELASYON ISI HARİTASI", fontsize=20, fontweight='bold', pad=25)
    
    # Alt Bilgi
    plt.figtext(0.5, 0.02, "Slayt 4 | Özellik Mühendisliği & Değişken İlişkileri Matrisi", 
                fontsize=12, style='italic', color=COLORS['gray'], ha='center')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "korelasyon_matrisi.png"), bbox_inches='tight', facecolor=COLORS['light_bg'])
    plt.close()
    print("Korelasyon Matrisi Isı Haritası Kaydedildi.")


# =============================================================================
# 4. MODEL PERFORMANS KARŞILAŞTIRMA GRAFİĞİ (Slayt 5)
# =============================================================================
def draw_model_performance_comparison():
    fig, ax = plt.subplots(figsize=(16, 9), dpi=120)
    ax.set_facecolor('white')
    fig.patch.set_facecolor(COLORS['light_bg'])
    
    # Model Verileri (XGBoost, Prophet, RF, LSTM, SVM, Isolation Forest)
    models = [
        'XGBoost\n(Sulama Kararı)', 'Prophet\n(Verim Tahmini)', 
        'Random Forest\n(Su Tüketimi)', 'LSTM\n(Uzun Dönem Nem)', 
        'SVM\n(Hastalık Tespit)', 'Isolation Forest\n(Anomali Tespiti)'
    ]
    
    target_scores = [0.90, 0.85, 0.85, 0.80, 0.80, 0.80]
    actual_scores = [0.893, 0.871, 0.856, 0.743, 0.778, 0.812]
    
    x = np.arange(len(models))
    width = 0.35
    
    # Çubukları Çiz
    rects_target = ax.bar(x - width/2, target_scores, width, label='Hedef Skor', color=COLORS['light_gray'], edgecolor=COLORS['gray'], linewidth=1)
    rects_actual = ax.bar(x + width/2, actual_scores, width, label='Gerçekleşen Skor', color=COLORS['primary'], edgecolor=COLORS['primary'], linewidth=1)
    
    # Skor Değerlerini Çubuk Üstlerine Yaz
    for rect in rects_target:
        h = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., h + 0.01, f"{h:.2f}", ha='center', va='bottom', fontsize=10, color=COLORS['gray'])
        
    for rect in rects_actual:
        h = rect.get_height()
        # Hedefi geçenleri yeşil, geçemeyenleri lacivert/turuncu yap
        color = COLORS['accent'] if h >= target_scores[int(rect.get_x() + 0.5)] else COLORS['warning']
        # LSTM çok düşükse kırmızı
        if h < 0.75:
            color = COLORS['error']
        rect.set_color(color)
        ax.text(rect.get_x() + rect.get_width()/2., h + 0.01, f"{h:.3f}", ha='center', va='bottom', fontsize=10, fontweight='bold', color=color)

    # Grafik Süslemesi
    ax.set_title("MODELLERİN ÇAPRAZ DOĞRULAMA (CV) SKORLARI VS HEDEF EŞİKLERİ", fontsize=20, fontweight='bold', pad=20)
    ax.set_ylabel("Skor Değeri (F1 Score veya R2)", fontsize=14, labelpad=10)
    ax.set_xticks(x)
    ax.set_xticklabels(models, fontsize=11, fontweight='bold')
    ax.set_ylim(0, 1.05)
    ax.grid(axis='y', linestyle=':', alpha=0.6, color=COLORS['gray'])
    ax.legend(fontsize=12, loc='upper right')
    
    # Açıklamalar
    ax.text(5.0, 0.4, "* F1 Skor: XGBoost, SVM, Isolation Forest\n* R2 Skor: Prophet, RF, LSTM", 
            bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.2), fontsize=10, color=COLORS['gray'])

    # Alt Bilgi
    plt.figtext(0.5, 0.02, "Slayt 5 | ML Modelleri Performans & Validasyon Karşılaştırması", 
                fontsize=12, style='italic', color=COLORS['gray'], ha='center')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "model_performans_karsilastirma.png"), bbox_inches='tight', facecolor=COLORS['light_bg'])
    plt.close()
    print("Model Performans Karşılaştırma Çubuk Grafiği Kaydedildi.")


# =============================================================================
# 5. ÇAPRAZ DOĞRULAMA (CV) SONUÇ DAĞILIMI BOX PLOT GRAFİĞİ (Slayt 6)
# =============================================================================
def draw_cv_score_distribution():
    fig, ax = plt.subplots(figsize=(16, 9), dpi=120)
    ax.set_facecolor('white')
    fig.patch.set_facecolor(COLORS['light_bg'])
    
    # 5 Fold CV Skor Dağılımları Simülasyonu
    data = {
        'XGBoost\n(Sulama)':    [0.871, 0.885, 0.912, 0.903, 0.894],
        'Prophet\n(Verim)':     [0.852, 0.838, 0.891, 0.904, 0.870],
        'Random Forest\n(Su)':   [0.825, 0.849, 0.884, 0.865, 0.857],
        'LSTM\n(Zaman Serisi)': [0.672, 0.718, 0.795, 0.781, 0.749],
        'SVM\n(Hastalık)':      [0.724, 0.768, 0.822, 0.795, 0.781]
    }
    df = pd.DataFrame(data)
    
    # Box plot çizimi (Seaborn)
    box_plot = sns.boxplot(data=df, width=0.4, palette=[COLORS['primary'], COLORS['accent'], COLORS['accent'], COLORS['error'], COLORS['warning']], linewidth=2)
    
    # Fold veri noktalarını jitter ile göster
    sns.stripplot(data=df, color=COLORS['gray'], size=8, jitter=0.1, alpha=0.8, edgecolor='black', linewidth=1)
    
    ax.set_title("5-FOLD ÇAPRAZ DOĞRULAMA SONUÇ DAĞILIMI VE VARYANS ANALİZİ", fontsize=20, fontweight='bold', pad=20)
    ax.set_ylabel("Validasyon Skoru", fontsize=14, labelpad=10)
    ax.set_ylim(0.55, 0.98)
    ax.grid(axis='y', linestyle=':', alpha=0.6, color=COLORS['gray'])
    
    # Alt Bilgi
    plt.figtext(0.5, 0.02, "Slayt 6 | Model Genelleme Yeteneği & Fold Bazlı Varyans Analizi", 
                fontsize=12, style='italic', color=COLORS['gray'], ha='center')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "cv_skor_dagilimi.png"), bbox_inches='tight', facecolor=COLORS['light_bg'])
    plt.close()
    print("CV Skor Dağılım Box Plot Grafiği Kaydedildi.")


# =============================================================================
# 6. KPI DASHBOARD GÖSTERGELERİ (Slayt 9)
# =============================================================================
def draw_kpi_dashboard():
    fig, ax = plt.subplots(figsize=(16, 9), dpi=120)
    ax.set_facecolor('white')
    fig.patch.set_facecolor(COLORS['light_bg'])
    
    # KPI Verileri
    kpis = [
        "Su Tüketim Tasarrufu\n(Hedef >%20)",
        "API Yanıt Süresi (P95)\n(Hedef <200ms)",
        "Sensör Veri Kalitesi\n(Hedef >%95)",
        "Sprint Tamamlanma Oranı\n(Hedef >%85)"
    ]
    
    # 0 ile 100 arasında normalize edilmiş değerler (Görselleştirme için)
    targets = [20.0, 100.0 - 200.0/4.0, 95.0, 85.0]  # API süresinde düşük olması iyi olduğundan normalize edildi
    realized = [23.7, 100.0 - 147.0/4.0, 96.4, 91.0]
    
    # Gerçek değerler (Etiketler için)
    real_target_labels = ["> %20", "< 200 ms", "> %95", "> %85"]
    real_actual_labels = ["%23.7 (Aşıldı)", "147 ms (Aşıldı)", "%96.4 (Aşıldı)", "%91.0 (Aşıldı)"]
    
    y = np.arange(len(kpis))
    height = 0.35
    
    # Yatay çubukları çiz
    rects_target = ax.barh(y + height/2, targets, height, label='Hedef KPI', color=COLORS['light_gray'], edgecolor=COLORS['gray'])
    rects_actual = ax.barh(y - height/2, realized, height, label='Gerçekleşen Başarı', color=COLORS['accent'], edgecolor=COLORS['accent'])
    
    # Çubukların üstüne/yanına değerleri yaz
    for i, rect in enumerate(rects_target):
        ax.text(rect.get_width() + 1.0, rect.get_y() + rect.get_height()/2., 
                f"Hedef: {real_target_labels[i]}", ha='left', va='center', fontsize=11, color=COLORS['gray'])
        
    for i, rect in enumerate(rects_actual):
        ax.text(rect.get_width() + 1.0, rect.get_y() + rect.get_height()/2., 
                real_actual_labels[i], ha='left', va='center', fontsize=12, fontweight='bold', color=COLORS['accent'])

    ax.set_title("PROJE KRİTİK KPI PERFORMANS GÖSTERGE PANELİ", fontsize=20, fontweight='bold', pad=25)
    ax.set_yticks(y)
    ax.set_yticklabels(kpis, fontsize=12, fontweight='bold')
    ax.set_xlim(0, 125)
    ax.axis('on')
    # X eksenini gizle (Normalize olduğu için kafa karıştırmasın)
    ax.get_xaxis().set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_color(COLORS['primary'])
    ax.legend(fontsize=12, loc='lower right')
    
    # Öne çıkan başarılar metni
    text_box = (
        "★ Öne Çıkan Başarılar:\n"
        "• Yıllık 340 Ton Su Tasarrufu Sağlandı (%23.7 tasarruf ile hedefin %18.5 üzerinde).\n"
        "• API Yanıt Süresi 147 ms ile hedefin %26.5 altında kalarak 3x yük taşıma kapasitesine ulaştı.\n"
        "• Sensör veri kalitesi %96.4 ile IoT hattı güvenilirliğini kanıtladı."
    )
    ax.text(5, -0.8, text_box, fontsize=11, color=COLORS['primary'], 
            bbox=dict(boxstyle="round,pad=0.5", fc=COLORS['light_gray'], alpha=0.5))

    # Alt Bilgi
    plt.figtext(0.5, 0.02, "Slayt 9 | Proje KPI Sonuçları & Hedef Karşılaştırması", 
                fontsize=12, style='italic', color=COLORS['gray'], ha='center')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "kpi_dashboard.png"), bbox_inches='tight', facecolor=COLORS['light_bg'])
    plt.close()
    print("KPI Gösterge Paneli Grafiği Kaydedildi.")


# =============================================================================
# 7. PROJE YOL HARİTASI (Slayt 10)
# =============================================================================
def draw_project_roadmap():
    fig, ax = plt.subplots(figsize=(16, 9), dpi=120)
    ax.set_facecolor(COLORS['light_bg'])
    fig.patch.set_facecolor(COLORS['light_bg'])
    
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    plt.axis('off')
    
    # Başlık
    ax.text(8, 8.2, "PROJE GELECEK YOL HARİTASI VE STRATEJİK HEDEFLER", 
            fontsize=24, fontweight='bold', color=COLORS['primary'], ha='center')
    
    # Dönemler
    phases = [
        # (x, y, w, h, dönem, zaman, hedefler, kriter, renk)
        (1.0, 1.5, 4.2, 5.5, "KISA VADE", "0 - 3 Ay", 
         "• LSTM modeli iyileştirmesi\n• SVM yerine XGBoost geçişi\n• Mobil uygulama beta yayını\n• 50 test kullanıcısı", 
         "Başarı Kriteri:\nF1 > 0.85, 50 Aktif Beta", COLORS['primary']),
         
        (5.9, 1.5, 4.2, 5.5, "ORTA VADE", "3 - 9 Ay", 
         "• Çoklu arazi entegrasyonu\n• Federe öğrenme altyapısı\n• Hava durumu API genişlemesi\n• Bölgesel tahmin modelleri", 
         "Başarı Kriteri:\n10 Arazi, %95 Doğruluk", COLORS['accent']),
         
        (10.8, 1.5, 4.2, 5.5, "UZUN VADE", "9 - 18 Ay", 
         "• Drone görüntü entegrasyonu\n• Karbon ayak izi hesaplama\n• Ulusal ölçekte pilot çalışma\n• Bakanlık API entegrasyonu", 
         "Başarı Kriteri:\nBakanlık Ortaklığı & Pilot", COLORS['warning'])
    ]
    
    for x, y, w, h, title, time_frame, goals, criteria, color in phases:
        # Kart çizimi
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1", 
                                      linewidth=2, edgecolor=color, facecolor='white', zorder=2)
        ax.add_patch(rect)
        
        # Kart Başlığı Şeridi
        header = patches.FancyBboxPatch((x, y+h-0.8), w, 0.8, boxstyle="round,pad=0.1", 
                                         linewidth=0, facecolor=color, zorder=3)
        ax.add_patch(header)
        
        # Başlık ve Zaman
        ax.text(x + w/2, y + h - 0.3, title, fontsize=16, fontweight='bold', color='white', ha='center', zorder=4)
        ax.text(x + w/2, y + h - 0.6, time_frame, fontsize=12, color='white', alpha=0.9, ha='center', zorder=4)
        
        # Hedefler Metni
        ax.text(x + 0.3, y + h - 1.2, goals, fontsize=11, color=COLORS['primary'], ha='left', va='top', zorder=4)
        
        # Başarı Kriteri Kutusu
        crit_box = patches.FancyBboxPatch((x+0.25, y+0.3), w-0.5, 1.0, boxstyle="round,pad=0.05", 
                                          linewidth=1, edgecolor=color, facecolor=COLORS['light_bg'], zorder=3)
        ax.add_patch(crit_box)
        ax.text(x + w/2, y + 0.8, criteria, fontsize=10, fontweight='bold', color=color, ha='center', va='center', zorder=4)
        
    # Bağlantı okları çizimi
    ax.arrow(5.3, 4.0, 0.4, 0.0, head_width=0.2, head_length=0.15, fc=COLORS['gray'], ec=COLORS['gray'], zorder=1)
    ax.arrow(10.2, 4.0, 0.4, 0.0, head_width=0.2, head_length=0.15, fc=COLORS['gray'], ec=COLORS['gray'], zorder=1)
    
    # Alt Bilgi
    plt.figtext(0.5, 0.02, "Slayt 10 | Sonraki Adımlar & Zaman Çizelgesi Yol Haritası", 
                fontsize=12, style='italic', color=COLORS['gray'], ha='center')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "proje_yol_haritasi.png"), bbox_inches='tight', facecolor=COLORS['light_bg'])
    plt.close()
    print("Proje Yol Haritası Çizelgesi Kaydedildi.")


if __name__ == "__main__":
    print("=" * 70)
    print("   SUNUM GÖRSELLERİ ÜRETİLİYOR...")
    print("=" * 70)
    
    draw_system_architecture()
    draw_sensor_trends()
    draw_correlation_matrix()
    draw_model_performance_comparison()
    draw_cv_score_distribution()
    draw_kpi_dashboard()
    draw_project_roadmap()
    
    print("=" * 70)
    print("   TÜM GÖRSELLER BAŞARIYLA ÜRETİLDİ!")
    print("=" * 70)
