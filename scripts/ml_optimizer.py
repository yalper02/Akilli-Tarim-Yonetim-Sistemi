import os
import sys
import django
import joblib
import optuna
import matplotlib.pyplot as plt
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, train_test_split
from optuna.visualization.matplotlib import plot_optimization_history, plot_param_importances

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from visualization.models import SensorData, Parcel

def prepare_data():
    print("Veritabanından veriler çekiliyor...")
    data_points = SensorData.objects.all()
    
    X = []
    y = []
    
    for d in data_points:
        if d.parcel:
            # Girdi: Sıcaklık, Nem, Toprak Nemi
            X.append([d.temperature, d.humidity, d.soil_moisture])
            # Hedef: Parselin şu anki sulama durumu
            y.append(1 if d.parcel.is_irrigating else 0)
            
    X = np.array(X)
    y = np.array(y)
    
    # Sentetik veri koruması (Veri çok azsa veya y'de sadece 0 varsa CV çöker)
    if len(X) < 20 or len(np.unique(y)) < 2:
        print("Uyarı: Yeterli varyasyon bulunamadı. Sentetik eğitim verisi (Mock Data) ekleniyor...")
        synth_X = np.random.uniform(low=[10.0, 30.0, 10.0], high=[40.0, 80.0, 90.0], size=(100, 3))
        synth_y = np.array([1 if moist < 30 else 0 for _, _, moist in synth_X])
        X = np.vstack((X, synth_X)) if len(X) > 0 else synth_X
        y = np.concatenate((y, synth_y)) if len(y) > 0 else synth_y

    return X, y

def objective(trial, X, y):
    # Optuna parametre uzayı tasarımı
    n_estimators = trial.suggest_int('n_estimators', 10, 500)
    max_depth = trial.suggest_int('max_depth', 2, 32)
    min_samples_split = trial.suggest_int('min_samples_split', 2, 10)
    
    model = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        min_samples_split=min_samples_split,
        random_state=42,
        n_jobs=-1
    )
    
    # 5-Katlı Çapraz Doğrulama
    scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
    return scores.mean()

def run_optimization():
    print("🚀 ATYS Optuna Hyperparameter Optimization Başlatılıyor...")
    X, y = prepare_data()
    
    print(f"Eğitim Seti Boyutu: {len(X)} Örnek")
    
    study = optuna.create_study(direction='maximize')
    study.optimize(lambda trial: objective(trial, X, y), n_trials=20)  # Demo için 20 trial yeterli
    
    print("\n✅ Optimizasyon Tamamlandı!")
    print(f"En İyi Doğruluk Skoru (Accuracy): %{study.best_value * 100:.2f}")
    print("En İyi Parametreler:")
    for key, value in study.best_params.items():
        print(f"  - {key}: {value}")
        
    # En iyi modelin son eğitimi
    best_model = RandomForestClassifier(**study.best_params, random_state=42)
    best_model.fit(X, y)
    
    # Dizinleri oluştur ve modeli kaydet
    models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
    os.makedirs(models_dir, exist_ok=True)
    
    model_path = os.path.join(models_dir, "optimized_irrigation_model.joblib")
    joblib.dump(best_model, model_path)
    print(f"💾 Final Model Kaydedildi: {model_path}")
    
    # Optuna grafiklerini kaydet
    media_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "media", "optimization_results")
    os.makedirs(media_dir, exist_ok=True)
    
    fig_history = plot_optimization_history(study)
    plt.savefig(os.path.join(media_dir, "optimization_history.png"))
    plt.close()
    
    fig_importances = plot_param_importances(study)
    plt.tight_layout()
    plt.savefig(os.path.join(media_dir, "param_importances.png"))
    plt.close()
    
    print(f"📊 Optimizasyon Grafikleri Kaydedildi: {media_dir}")

if __name__ == "__main__":
    # Optuna loglarını biraz temiz tutmak için
    optuna.logging.set_verbosity(optuna.logging.INFO)
    run_optimization()
