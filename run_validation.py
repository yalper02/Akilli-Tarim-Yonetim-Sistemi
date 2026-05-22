import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.tree import DecisionTreeClassifier
from sklearn.calibration import CalibrationDisplay
from model_validation import ModelValidator, ValidationDiagnostic, PipelineMonitor, calculate_all_metrics

def generate_agricultural_data(n_samples: int = 1000, random_state: int = 42) -> Tuple[pd.DataFrame, pd.Series, np.ndarray]:
    """
    Tarım uygulamaları için sentetik veri seti oluşturur.
    
    Özellikler:
        - toprak_nemi: % nem
        - hava_sicakligi: C derece
        - hava_nemi: % nem
        - ruzgar_hizi: km/s
        - son_yagis: mm
        - tarla_id: Tarla grupları (Group K-Fold için)
        
    Hedef:
        - sulama_karari (Sınıflandırma: 1 (Sula), 0 (Sulamayı Durdur))
    """
    np.random.seed(random_state)
    
    # Sensör özellikleri
    toprak_nemi = np.random.uniform(10.0, 90.0, n_samples)
    hava_sicakligi = np.random.uniform(15.0, 42.0, n_samples)
    hava_nemi = np.random.uniform(20.0, 85.0, n_samples)
    ruzgar_hizi = np.random.uniform(0.0, 25.0, n_samples)
    son_yagis = np.random.exponential(scale=5.0, size=n_samples)
    
    # Tarla ID'leri (10 farklı tarla)
    tarla_id = np.random.randint(1, 11, n_samples)
    
    # Sulama Kararı Hedefi (Toprak nemi ve sıcaklığa bağlı mantık + gürültü)
    # Nem < 35 ve sıcaklık > 25 ise genellikle sulama gerekir
    logit = -0.15 * (toprak_nemi - 35) + 0.1 * (hava_sicakligi - 25) - 0.05 * hava_nemi + np.random.normal(0, 1.5, n_samples)
    prob = 1 / (1 + np.exp(-logit))
    sulama_karari = (prob > 0.5).astype(int)
    
    # Verim Tahmini Hedefi (Regresyon için)
    # Nem, sıcaklık ve yağışla pozitif, aşırı rüzgarla negatif ilişkili verim tahmini
    verim = 150 + 2.5 * toprak_nemi + 1.2 * hava_nemi + 5.0 * son_yagis - 0.8 * ruzgar_hizi + np.random.normal(0, 15, n_samples)
    
    df = pd.DataFrame({
        'toprak_nemi': toprak_nemi,
        'hava_sicakligi': hava_sicakligi,
        'hava_nemi': hava_nemi,
        'ruzgar_hizi': ruzgar_hizi,
        'son_yagis': son_yagis
    })
    
    return df, pd.Series(sulama_karari), tarla_id, pd.Series(verim)


def main():
    print("=" * 70)
    print("   AKILLI TARIM YÖNETİM SİSTEMİ - MODEL VALIDASYON VE DOĞRULAMA TESTİ")
    print("=" * 70)
    
    # 1. Dizin Kurulumu
    media_dir = "media"
    os.makedirs(media_dir, exist_ok=True)
    
    # 2. Veri Üretimi
    print("\n[Adım 1] Sentetik Tarımsal Veri Seti Üretiliyor...")
    X, y_class, tarlalar, y_reg = generate_agricultural_data(n_samples=800)
    print(f"Toplam Veri Sayısı: {len(X)}")
    print(f"Sınıf Dağılımı (Sulama Kararı): 0 -> {(y_class == 0).sum()}, 1 -> {(y_class == 1).sum()}")
    print(f"Regresyon Hedef Dağılımı (Verim): Min={y_reg.min():.2f}, Max={y_reg.max():.2f}, Ortalama={y_reg.mean():.2f}")
    
    # 3. Model Validasyon Yöntemleri
    print("\n[Adım 2] Model Validasyon Yöntemleri Çalıştırılıyor...")
    
    # A) Sınıflandırma Modeli: Random Forest Classifier
    rf_clf = RandomForestClassifier(n_estimators=50, max_depth=6, random_state=42)
    validator_clf = ModelValidator(rf_clf, X, y_class, is_regression=False)
    
    # A.1) Stratified 10-Fold CV
    cv_stratified = validator_clf.validate_stratified_k_fold(k=10)
    print("\n--- Stratified 10-Fold CV (Sulama Kararı) ---")
    print(f"Ortalama Train F1 Skor (Macro): {cv_stratified['mean_train_score']:.4f}")
    print(f"Ortalama CV F1 Skor (Macro): {cv_stratified['mean_val_score']:.4f} ± {cv_stratified['std_val_score']:.4f}")
    print("Genel Güven Aralıklı Metrikler:")
    for met, info in cv_stratified['overall_metrics'].items():
        print(f"  - {met.upper()}: {info['val']:.4f} (%95 GA: [{info['lower']:.4f}, {info['upper']:.4f}])")
        
    # A.2) Group K-Fold CV (Tarla/Sensör Bağımsızlığı)
    cv_group = validator_clf.validate_group_k_fold(groups=tarlalar, k=5)
    print("\n--- Group K-Fold CV (Tarla Bağımsızlığı, k=5) ---")
    print(f"Ortalama Train F1 Skor: {cv_group['mean_train_score']:.4f}")
    print(f"Ortalama CV F1 Skor: {cv_group['mean_val_score']:.4f} ± {cv_group['std_val_score']:.4f}")
    
    # A.3) Nested CV (Parametre Arama ve Değerlendirme)
    param_grid = {
        'n_estimators': [20, 50],
        'max_depth': [4, 8]
    }
    cv_nested = validator_clf.validate_nested_cv(param_grid, inner_k=3, outer_k=3)
    print("\n--- Nested CV (Optimizasyonlu Parametre Seçimi) ---")
    print(f"Ortalama Train Skoru: {cv_nested['mean_train_score']:.4f}")
    print(f"Ortalama CV Skoru (Genelleme Yeteneği): {cv_nested['mean_val_score']:.4f} ± {cv_nested['std_val_score']:.4f}")
    
    # B) Zaman Serisi / Regresyon Modeli: Random Forest Regressor
    rf_reg = RandomForestRegressor(n_estimators=50, max_depth=6, random_state=42)
    # Zaman sırasını simüle etmek için veriyi sıralayalım
    X_sorted = X.sort_index()
    y_reg_sorted = y_reg.sort_index()
    validator_reg = ModelValidator(rf_reg, X_sorted, y_reg_sorted, is_regression=True)
    
    # B.1) Time Series Split
    cv_ts = validator_reg.validate_time_series_split(n_splits=5)
    print("\n--- Time Series Split CV (Verim Tahmini, n_splits=5) ---")
    print(f"Ortalama Train R2 Skor: {cv_ts['mean_train_score']:.4f}")
    print(f"Ortalama CV R2 Skor: {cv_ts['mean_val_score']:.4f} ± {cv_ts['std_val_score']:.4f}")
    print("Genel Güven Aralıklı Metrikler:")
    for met, info in cv_ts['overall_metrics'].items():
        print(f"  - {met.upper()}: {info['val']:.4f} (%95 GA: [{info['lower']:.4f}, {info['upper']:.4f}])")
        
    # 4. Hata Teşhis Motoru Testleri
    print("\n[Adım 3] Hata Teşhis ve Sağlık Kontrolleri (Diagnostic Engine) Çalıştırılıyor...")
    diagnostic = ValidationDiagnostic(target_threshold=0.85)
    
    # Durum 1: Başarılı Model Teşhisi (Random Forest)
    print("\n>>> Senaryo 1: Sağlıklı Random Forest Modeli Teşhisi")
    report_healthy = diagnostic.diagnose(
        mean_train=cv_stratified['mean_train_score'],
        mean_cv=cv_stratified['mean_val_score'],
        std_cv=cv_stratified['std_val_score']
    )
    if not report_healthy:
        print("[OK] Model Sagligi: Mukemmel! Herhangi bir anomali tespit edilmedi.")
    else:
        for diag in report_healthy:
            print(f"[{diag['level']}] {diag['issue']}: {diag['metric']}\n   Oneri: {diag['solution']}")
            
    # Durum 2: Overfitting Teşhisi Simülasyonu
    print("\n>>> Senaryo 2: Aşırı Öğrenme (Overfitting) Simülasyonu")
    # Çok derin karar ağacı gürültülü veride overfitting yapar
    overfitted_tree = DecisionTreeClassifier(max_depth=30, random_state=42)
    validator_of = ModelValidator(overfitted_tree, X, y_class, is_regression=False)
    cv_of = validator_of.validate_k_fold(k=5)
    
    report_of = diagnostic.diagnose(
        mean_train=cv_of['mean_train_score'],
        mean_cv=cv_of['mean_val_score'],
        std_cv=cv_of['std_val_score']
    )
    for diag in report_of:
        print(f"[{diag['level']}] {diag['issue']}: {diag['metric']}\n   Öneri: {diag['solution']}")
        # Slack uyarısı tetikle
        PipelineMonitor.send_slack_alert(diag['issue'], diag['metric'], diag['level'])
        
    # Durum 3: Veri Sızıntısı (Data Leakage) Simülasyonu
    print("\n>>> Senaryo 3: Veri Sızıntısı (Data Leakage) Simülasyonu")
    # Veri setine hedef değişkenin aynısını özellik olarak ekliyoruz!
    X_leaked = X.copy()
    X_leaked['leak_feature'] = y_class.values
    validator_leak = ModelValidator(rf_clf, X_leaked, y_class, is_regression=False)
    cv_leak = validator_leak.validate_k_fold(k=5)
    
    report_leak = diagnostic.diagnose(
        mean_train=cv_leak['mean_train_score'],
        mean_cv=cv_leak['mean_val_score'],
        std_cv=cv_leak['std_val_score']
    )
    for diag in report_leak:
        print(f"[{diag['level']}] {diag['issue']}: {diag['metric']}\n   Öneri: {diag['solution']}")
        
    # Durum 4: Dağılım Kayması (Drift) Simülasyonu
    print("\n>>> Senaryo 4: Dağılım Kayması (Drift) Analizi")
    # Üretim verisi ile eğitim verisi arasındaki skor farkı
    report_drift = diagnostic.diagnose(
        mean_train=0.88,
        mean_cv=0.86,
        std_cv=0.02,
        prod_score=0.74 # Büyük bir performans düşüşü
    )
    for diag in report_drift:
        print(f"[{diag['level']}] {diag['issue']}: {diag['metric']}\n   Öneri: {diag['solution']}")
        
    # Evidently AI Entegrasyon Simülasyonu
    drift_details = PipelineMonitor.run_evidently_drift_analysis(X, X * 1.5)
    print(f"Evidently AI PSI Skoru: {drift_details['psi']:.2f} (Durum: {drift_details['status']})")
    
    # 5. Görselleştirme: Eğitim/Validasyon Fark Grafiği ve Kalibrasyon Eğrisi
    print("\n[Adım 4] Görselleştirme Grafikleri media/ klasörüne kaydediliyor...")
    
    # A) Overfitting Fark Grafiği
    plt.figure(figsize=(8, 5))
    models = ['Sağlıklı Model (RF)', 'Aşırı Öğrenen Model (Tree)']
    train_scores = [cv_stratified['mean_train_score'], cv_of['mean_train_score']]
    val_scores = [cv_stratified['mean_val_score'], cv_of['mean_val_score']]
    
    x = np.arange(len(models))
    width = 0.35
    
    plt.bar(x - width/2, train_scores, width, label='Train Skoru', color='#4f46e5')
    plt.bar(x + width/2, val_scores, width, label='CV Skoru', color='#10b981')
    
    plt.ylabel('F1 Skor (Macro)')
    plt.title('Eğitim vs Çapraz Doğrulama Performansı Karşılaştırması')
    plt.xticks(x, models)
    plt.ylim(0, 1.1)
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(media_dir, "train_cv_performance_comparison.png"))
    plt.close()
    print(f"[PLOT] Performans Karsilastirma Grafigi Kaydedildi: {os.path.join(media_dir, 'train_cv_performance_comparison.png')}")
    
    # B) Kalibrasyon Eğrisi Grafiği (Calibration Curve)
    # Modeli eğitelim ve test setindeki kalibrasyonu çizelim
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y_class, test_size=0.3, random_state=42)
    rf_clf.fit(X_train, y_train)
    prob_pos = rf_clf.predict_proba(X_test)[:, 1]
    
    fig, ax = plt.subplots(figsize=(8, 6))
    CalibrationDisplay.from_predictions(y_test, prob_pos, n_bins=10, name="Random Forest Classifier", ax=ax)
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.set_title("Olasılık Kalibrasyon Eğrisi (Sulama Kararı Modeli)")
    
    plt.tight_layout()
    plt.savefig(os.path.join(media_dir, "model_calibration_curve.png"))
    plt.close()
    print(f"[PLOT] Model Kalibrasyon Egrisi Kaydedildi: {os.path.join(media_dir, 'model_calibration_curve.png')}")
    
    # MLflow mock loglama testi
    PipelineMonitor.log_to_mlflow(
        metrics={'cv_f1_macro': cv_stratified['mean_val_score'], 'train_f1_macro': cv_stratified['mean_train_score']},
        params={'n_estimators': 50, 'max_depth': 6},
        artifact_paths=[os.path.join(media_dir, 'model_calibration_curve.png')]
    )

    print("\n" + "=" * 70)
    print("   DOĞRULAMA TESTLERİ BAŞARIYLA TAMAMLANDI!")
    print("=" * 70)

if __name__ == "__main__":
    main()
