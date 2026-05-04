import os
import sys
import django
import joblib
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.calibration import CalibratedClassifierCV, CalibrationDisplay
from sklearn.metrics import brier_score_loss

# Setup Django environment to fetch data
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from visualization.models import SensorData

def prepare_data():
    data_points = SensorData.objects.all()
    X = []
    y = []
    for d in data_points:
        if d.parcel:
            X.append([d.temperature, d.humidity, d.soil_moisture])
            y.append(1 if d.parcel.is_irrigating else 0)
            
    X = np.array(X)
    y = np.array(y)
    
    # Sentetik veri koruması (Veri çok azsa veya y'de sadece 0 varsa)
    if len(X) < 50 or len(np.unique(y)) < 2:
        print("Uyarı: Yeterli gerçek veri bulunamadı. Sentetik verilerle destekleniyor...")
        synth_X = np.random.uniform(low=[10.0, 30.0, 10.0], high=[40.0, 80.0, 90.0], size=(500, 3))
        synth_y = np.array([1 if moist < 30 else 0 for _, _, moist in synth_X])
        X = np.vstack((X, synth_X)) if len(X) > 0 else synth_X
        y = np.concatenate((y, synth_y)) if len(y) > 0 else synth_y

    return train_test_split(X, y, test_size=0.3, random_state=42)

def run_calibration():
    print("🚀 Model Kalibrasyonu ve Güven Analizi Başlatılıyor...")
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_path = os.path.join(base_dir, "models", "optimized_irrigation_model.joblib")
    
    if not os.path.exists(model_path):
        print(f"HATA: Temel model bulunamadı! Önce ml_optimizer.py çalıştırılmalıdır.\nAranan yol: {model_path}")
        return

    # Orijinal modeli yükle
    base_model = joblib.load(model_path)
    X_train, X_test, y_train, y_test = prepare_data()

    # Orijinal model performansı
    base_model.fit(X_train, y_train)
    prob_base = base_model.predict_proba(X_test)[:, 1]
    brier_base = brier_score_loss(y_test, prob_base)
    print(f"\n📊 Orijinal Model Brier Score: {brier_base:.4f}")

    # Platt (Sigmoid) Kalibrasyonu
    calib_sigmoid = CalibratedClassifierCV(base_model, method='sigmoid', cv='prefit')
    calib_sigmoid.fit(X_test, y_test) # prefit olduğu için test veya validation setinde eğitilir
    prob_sigmoid = calib_sigmoid.predict_proba(X_test)[:, 1]
    brier_sigmoid = brier_score_loss(y_test, prob_sigmoid)
    print(f"📊 Platt (Sigmoid) Kalibrasyon Brier Score: {brier_sigmoid:.4f}")

    # Isotonic Kalibrasyonu
    calib_isotonic = CalibratedClassifierCV(base_model, method='isotonic', cv='prefit')
    calib_isotonic.fit(X_test, y_test)
    prob_isotonic = calib_isotonic.predict_proba(X_test)[:, 1]
    brier_isotonic = brier_score_loss(y_test, prob_isotonic)
    print(f"📊 Isotonic Kalibrasyon Brier Score: {brier_isotonic:.4f}\n")

    # En İyi Modeli Belirle (En düşük Brier Skoru en iyisidir)
    scores = {
        "Orijinal": (brier_base, base_model),
        "Platt (Sigmoid)": (brier_sigmoid, calib_sigmoid),
        "Isotonic": (brier_isotonic, calib_isotonic)
    }
    
    best_name = min(scores, key=lambda k: scores[k][0])
    best_score, best_model_to_save = scores[best_name]
    
    print(f"🏆 En İyi Model: {best_name} (Brier Score: {best_score:.4f})")
    
    # En İyi Modeli Kaydet
    calib_model_path = os.path.join(base_dir, "models", "calibrated_irrigation_model.joblib")
    joblib.dump(best_model_to_save, calib_model_path)
    print(f"💾 Kalibre Edilmiş En İyi Model Kaydedildi: {calib_model_path}")

    # Görselleştirme: Calibration Curve (Reliability Diagram)
    media_dir = os.path.join(base_dir, "media", "calibration_results")
    os.makedirs(media_dir, exist_ok=True)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # CalibrationDisplay ile grafikleri çizdir
    CalibrationDisplay.from_predictions(y_test, prob_base, n_bins=10, name="Orijinal Model", ax=ax)
    CalibrationDisplay.from_predictions(y_test, prob_sigmoid, n_bins=10, name="Platt (Sigmoid)", ax=ax)
    CalibrationDisplay.from_predictions(y_test, prob_isotonic, n_bins=10, name="Isotonic", ax=ax)
    
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.set_title("Calibration Curve (Reliability Diagram)")
    ax.set_xlabel("Mean Predicted Probability")
    ax.set_ylabel("Fraction of Positives")
    
    plot_path = os.path.join(media_dir, "calibration_curve.png")
    plt.tight_layout()
    plt.savefig(plot_path)
    plt.close()
    
    print(f"📈 Kalibrasyon Eğrisi Grafiği Kaydedildi: {plot_path}")

if __name__ == "__main__":
    run_calibration()
