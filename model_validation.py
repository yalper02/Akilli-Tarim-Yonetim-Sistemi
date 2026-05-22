import numpy as np
import pandas as pd
import logging
from typing import Dict, Any, List, Tuple, Callable, Optional
from sklearn.model_selection import KFold, StratifiedKFold, TimeSeriesSplit, GroupKFold, GridSearchCV
from sklearn.metrics import f1_score, r2_score, mean_absolute_percentage_error, roc_auc_score, root_mean_squared_error, matthews_corrcoef
from sklearn.base import clone, BaseEstimator

# Logging Konfigürasyonu
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ModelValidation")

# =============================================================================
# 1. METRİK VE BOOTSTRAP GÜVEN ARALIĞI HESAPLAMA
# =============================================================================

def bootstrap_metric_ci(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_prob: Optional[np.ndarray],
    metric_name: str,
    confidence: float = 0.95,
    n_bootstrap: int = 1000,
    random_state: int = 42
) -> Tuple[float, float]:
    """
    Belirli bir metrik için bootstrap yöntemiyle %95 güven aralığını hesaplar.
    
    Args:
        y_true: Gerçek etiketler/değerler.
        y_pred: Tahmin edilen etiketler/değerler.
        y_prob: Sınıflandırma olasılıkları (ROC-AUC için).
        metric_name: Metrik adı ('f1', 'r2', 'mape', 'roc_auc', 'rmse', 'mcc').
        confidence: Güven düzeyi (örn: 0.95).
        n_bootstrap: Bootstrap örnekleme sayısı.
        random_state: Rastgelelik tohumu.
        
    Returns:
        (alt_sinir, ust_sinir) olarak güven aralığı.
    """
    rng = np.random.default_rng(random_state)
    bootstrapped_scores = []
    n_samples = len(y_true)
    
    if n_samples == 0:
        return 0.0, 0.0

    for _ in range(n_bootstrap):
        # Örnek yerine koyarak yeniden örneklenir (resampling with replacement)
        indices = rng.choice(n_samples, size=n_samples, replace=True)
        
        # Sınıflandırma problemlerinde tek sınıf kalma riskini kontrol et
        if metric_name in ['f1', 'roc_auc', 'mcc'] and len(np.unique(y_true[indices])) < 2:
            continue
            
        try:
            if metric_name == 'f1':
                score = f1_score(y_true[indices], y_pred[indices], average='macro')
            elif metric_name == 'r2':
                score = r2_score(y_true[indices], y_pred[indices])
            elif metric_name == 'mape':
                score = mean_absolute_percentage_error(y_true[indices], y_pred[indices])
            elif metric_name == 'roc_auc':
                if y_prob is not None:
                    score = roc_auc_score(y_true[indices], y_prob[indices])
                else:
                    score = roc_auc_score(y_true[indices], y_pred[indices])
            elif metric_name == 'rmse':
                score = root_mean_squared_error(y_true[indices], y_pred[indices])
            elif metric_name == 'mcc':
                score = matthews_corrcoef(y_true[indices], y_pred[indices])
            else:
                raise ValueError(f"Bilinmeyen metrik: {metric_name}")
            
            bootstrapped_scores.append(score)
        except Exception as e:
            # Nadir hata durumlarında geç
            continue
            
    if len(bootstrapped_scores) == 0:
        return 0.0, 0.0
        
    # Güven aralığı yüzdelik dilimlerini hesapla
    lower_percentile = (1.0 - confidence) / 2.0 * 100
    upper_percentile = (1.0 + confidence) / 2.0 * 100
    
    lower_bound = np.percentile(bootstrapped_scores, lower_percentile)
    upper_bound = np.percentile(bootstrapped_scores, upper_percentile)
    
    return float(lower_bound), float(upper_bound)


def calculate_all_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_prob: Optional[np.ndarray] = None,
    is_regression: bool = False
) -> Dict[str, Dict[str, float]]:
    """
    Model çıktılarına göre tüm birincil ve yardımcı metrikleri güven aralığı ile hesaplar.
    
    Returns:
        Metrik adı -> {'val': değer, 'lower': alt_sınır, 'upper': üst_sınır}
    """
    results = {}
    
    if is_regression:
        metrics_to_calc = ['r2', 'mape', 'rmse']
    else:
        metrics_to_calc = ['f1', 'roc_auc', 'mcc']
        
    for metric in metrics_to_calc:
        try:
            if metric == 'f1':
                val = f1_score(y_true, y_pred, average='macro')
            elif metric == 'r2':
                val = r2_score(y_true, y_pred)
            elif metric == 'mape':
                val = mean_absolute_percentage_error(y_true, y_pred)
            elif metric == 'roc_auc':
                if y_prob is not None:
                    val = roc_auc_score(y_true, y_prob)
                else:
                    val = roc_auc_score(y_true, y_pred)
            elif metric == 'rmse':
                val = root_mean_squared_error(y_true, y_pred)
            elif metric == 'mcc':
                val = matthews_corrcoef(y_true, y_pred)
            
            lower, upper = bootstrap_metric_ci(y_true, y_pred, y_prob, metric)
            results[metric] = {'val': float(val), 'lower': lower, 'upper': upper}
        except Exception as e:
            logger.error(f"Metrik hesaplama hatası ({metric}): {str(e)}")
            results[metric] = {'val': 0.0, 'lower': 0.0, 'upper': 0.0}
            
    return results


# =============================================================================
# 2. ÇAPRAZ DOĞRULAMA (CROSS-VALIDATION) YÖNTEMLERİ
# =============================================================================

class ModelValidator:
    """
    Farklı Çapraz Doğrulama (CV) stratejilerini yöneten ve sonuçları derleyen sınıf.
    """
    def __init__(self, model: BaseEstimator, X: pd.DataFrame, y: pd.Series, is_regression: bool = False):
        self.model = model
        self.X = X
        self.y = y
        self.is_regression = is_regression
        
    def _run_cv(self, cv_iterator) -> Dict[str, Any]:
        """Genel CV çalıştırıcı şablonu."""
        fold_metrics = []
        train_scores = []
        val_scores = []
        
        y_true_all = []
        y_pred_all = []
        y_prob_all = []
        
        primary_metric = 'r2' if self.is_regression else 'f1'
        
        for fold, (train_idx, val_idx) in enumerate(cv_iterator):
            X_train, X_val = self.X.iloc[train_idx], self.X.iloc[val_idx]
            y_train, y_val = self.y.iloc[train_idx], self.y.iloc[val_idx]
            
            # Model klonlanır ve eğitilir
            fold_model = clone(self.model)
            fold_model.fit(X_train, y_train)
            
            # Tahminler
            y_pred_train = fold_model.predict(X_train)
            y_pred_val = fold_model.predict(X_val)
            
            # Olasılıklar (Sınıflandırma ve ROC-AUC için)
            y_prob_val = None
            if not self.is_regression and hasattr(fold_model, "predict_proba"):
                try:
                    y_prob_val = fold_model.predict_proba(X_val)[:, 1]
                except Exception:
                    pass
            
            # Metrikleri hesapla
            val_results = calculate_all_metrics(y_val.values, y_pred_val, y_prob_val, self.is_regression)
            
            # Tren skorunu kaydet (Overfitting teşhisi için)
            if self.is_regression:
                train_score = r2_score(y_train, y_pred_train)
            else:
                train_score = f1_score(y_train, y_pred_train, average='macro')
                
            train_scores.append(train_score)
            val_scores.append(val_results[primary_metric]['val'])
            
            fold_metrics.append({
                'fold': fold + 1,
                'train_score': train_score,
                'val_metrics': val_results
            })
            
            y_true_all.extend(y_val.values)
            y_pred_all.extend(y_pred_val)
            if y_prob_val is not None:
                y_prob_all.extend(y_prob_val)
                
        # Genel (Havuzlanmış) Performans
        y_true_all = np.array(y_true_all)
        y_pred_all = np.array(y_pred_all)
        y_prob_all = np.array(y_prob_all) if len(y_prob_all) > 0 else None
        
        overall_metrics = calculate_all_metrics(y_true_all, y_pred_all, y_prob_all, self.is_regression)
        
        return {
            'folds_detail': fold_metrics,
            'mean_train_score': float(np.mean(train_scores)),
            'mean_val_score': float(np.mean(val_scores)),
            'std_val_score': float(np.std(val_scores)),
            'overall_metrics': overall_metrics
        }
        
    def validate_k_fold(self, k: int = 5, shuffle: bool = True, random_state: int = 42) -> Dict[str, Any]:
        """K-Fold Çapraz Doğrulama."""
        logger.info(f"K-Fold CV başlatılıyor (k={k})...")
        kf = KFold(n_splits=k, shuffle=shuffle, random_state=random_state)
        return self._run_cv(kf.split(self.X))
        
    def validate_stratified_k_fold(self, k: int = 5, shuffle: bool = True, random_state: int = 42) -> Dict[str, Any]:
        """Stratified K-Fold Çapraz Doğrulama (Sınıf dengesizliği için)."""
        if self.is_regression:
            logger.warning("Stratified K-Fold regresyon için önerilmez. Standart K-Fold kullanılıyor.")
            return self.validate_k_fold(k, shuffle, random_state)
            
        logger.info(f"Stratified K-Fold CV başlatılıyor (k={k})...")
        skf = StratifiedKFold(n_splits=k, shuffle=shuffle, random_state=random_state)
        return self._run_cv(skf.split(self.X, self.y))
        
    def validate_time_series_split(self, n_splits: int = 5) -> Dict[str, Any]:
        """Time Series Split Çapraz Doğrulama (Zaman serisi / Sensör verileri için)."""
        logger.info(f"Time Series Split CV başlatılıyor (n_splits={n_splits})...")
        tscv = TimeSeriesSplit(n_splits=n_splits)
        return self._run_cv(tscv.split(self.X))
        
    def validate_group_k_fold(self, groups: np.ndarray, k: int = 5) -> Dict[str, Any]:
        """Group K-Fold Çapraz Doğrulama (Tarla/arazi bazlı bağımsız test için)."""
        logger.info(f"Group K-Fold CV başlatılıyor (k={k})...")
        gkf = GroupKFold(n_splits=k)
        return self._run_cv(gkf.split(self.X, self.y, groups))
        
    def validate_nested_cv(
        self,
        param_grid: Dict[str, List[Any]],
        inner_k: int = 5,
        outer_k: int = 5,
        random_state: int = 42
    ) -> Dict[str, Any]:
        """
        Nested CV (İç döngü: parametre arama, Dış döngü: performans ölçümü).
        """
        logger.info(f"Nested CV başlatılıyor (Dış={outer_k}, İç={inner_k})...")
        outer_cv = KFold(n_splits=outer_k, shuffle=True, random_state=random_state)
        
        outer_scores = []
        outer_train_scores = []
        
        primary_metric = 'r2' if self.is_regression else 'f1'
        scoring_metric = 'r2' if self.is_regression else 'f1_macro'
        
        for fold, (train_idx, val_idx) in enumerate(outer_cv.split(self.X)):
            X_train, X_val = self.X.iloc[train_idx], self.X.iloc[val_idx]
            y_train, y_val = self.y.iloc[train_idx], self.y.iloc[val_idx]
            
            # İç döngü için GridSearchCV (veya Optuna entegrasyonu)
            inner_cv = KFold(n_splits=inner_k, shuffle=True, random_state=random_state)
            grid_search = GridSearchCV(
                estimator=clone(self.model),
                param_grid=param_grid,
                cv=inner_cv,
                scoring=scoring_metric,
                n_jobs=-1
            )
            
            grid_search.fit(X_train, y_train)
            best_model = grid_search.best_estimator_
            
            # Dış döngü değerlendirmesi
            y_pred_train = best_model.predict(X_train)
            y_pred_val = best_model.predict(X_val)
            
            if self.is_regression:
                train_score = r2_score(y_train, y_pred_train)
                val_score = r2_score(y_val, y_pred_val)
            else:
                train_score = f1_score(y_train, y_pred_train, average='macro')
                val_score = f1_score(y_val, y_pred_val, average='macro')
                
            outer_train_scores.append(train_score)
            outer_scores.append(val_score)
            
            logger.info(f"Dış Fold {fold+1} tamamlandı. En iyi param: {grid_search.best_params_}, Val Skor: {val_score:.4f}")
            
        return {
            'mean_train_score': float(np.mean(outer_train_scores)),
            'mean_val_score': float(np.mean(outer_scores)),
            'std_val_score': float(np.std(outer_scores)),
            'outer_scores': outer_scores
        }


# =============================================================================
# 3. HATA TEŞHİS VE AŞIRI/AZ ÖĞRENME ANALİZİ
# =============================================================================

class ValidationDiagnostic:
    """
    Validasyon sonuçlarını analiz ederek overfitting, underfitting, sızıntı ve varyans tespiti yapar.
    """
    def __init__(self, target_threshold: float = 0.85):
        self.target_threshold = target_threshold

    def diagnose(
        self,
        mean_train: float,
        mean_cv: float,
        std_cv: float,
        prod_score: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Model performans kriterlerini inceleyerek teşhis raporu hazırlar.
        """
        diagnoses = []
        
        # 1. Overfitting (Aşırı Öğrenme)
        diff = mean_train - mean_cv
        if diff > 0.10:
            diagnoses.append({
                'level': 'WARNING',
                'issue': 'Aşırı Öğrenme (Overfitting)',
                'metric': f"Train-CV farkı: {diff:.4f} (> 0.10)",
                'solution': "L1/L2 regülarizasyonu ekleyin, ağaç derinliğini sınırlandırın (max_depth) veya Dropout uygulayın."
            })
            
        # 2. Underfitting (Az Öğrenme)
        if mean_cv < self.target_threshold:
            diagnoses.append({
                'level': 'WARNING',
                'issue': 'Az Öğrenme (Underfitting)',
                'metric': f"CV Skoru: {mean_cv:.4f} (Hedef Eşik: {self.target_threshold:.2f})",
                'solution': "Model karmaşıklığını artırın, yeni özellikler (features) türetin veya eğitimi uzatın."
            })
            
        # 3. High Variance (Yüksek Varyans)
        if std_cv > 0.05:
            diagnoses.append({
                'level': 'WARNING',
                'issue': 'Yüksek Varyans (Variance)',
                'metric': f"Foldlar arası standart sapma: {std_cv:.4f} (> 0.05)",
                'solution': "Ensemble (Bagging/Random Forest) yöntemleri kullanın, veri setini artırın veya çapraz doğrulamayı düzenleyin."
            })
            
        # 4. Data Leakage (Veri Sızıntısı)
        if mean_train > 0.99:
            diagnoses.append({
                'level': 'CRITICAL',
                'issue': 'Veri Sızıntısı (Data Leakage)',
                'metric': f"Train Skoru: {mean_train:.4f} (Anormal Derecede Yüksek)",
                'solution': "Hedef değişkenin türevlerinin girdi özniteliklerde bulunup bulunmadığını ve zaman serilerinde shuffle edilip edilmediğini kontrol edin."
            })
            
        # 5. Concept Drift / Distribution Shift (Dağılım Kayması)
        if prod_score is not None:
            drift_diff = mean_cv - prod_score
            if drift_diff > 0.08:
                diagnoses.append({
                    'level': 'CRITICAL',
                    'issue': 'Dağılım Kayması (Concept Drift)',
                    'metric': f"Prod ve CV skoru farkı: {drift_diff:.4f} (> 0.08)",
                    'solution': "Modeli en güncel verilerle yeniden eğitin, veri kalitesini inceleyin ve Evidently AI drift analizlerini tetikleyin."
                })
                
        return diagnoses


# =============================================================================
# 4. OTOMATİK İZLEME PİPELİNE'I VE UYARILAR
# =============================================================================

class PipelineMonitor:
    """
    Slack, MLflow ve İzleme kütüphanelerine entegrasyon arayüzleri.
    """
    @staticmethod
    def send_slack_alert(issue: str, details: str, level: str = 'WARNING') -> bool:
        """
        Slack webhook aracılığıyla uyarı gönderir (Simüle edilmiştir).
        """
        emoji_str = "[WARNING]" if level == 'WARNING' else "[CRITICAL]"
        message = f"{emoji_str} *ML Pipeline Uyarisi* [{level}]\n*Sorun:* {issue}\n*Detay:* {details}"
        logger.warning(f"[SLACK ALERT] {message.replace('*', '')}")
        return True

    @staticmethod
    def log_to_mlflow(metrics: Dict[str, float], params: Dict[str, Any], artifact_paths: List[str] = []):
        """
        MLflow sunucusuna metrik ve parametre kaydeder (Arayüz tasarımı).
        """
        logger.info("Logging to MLflow...")
        for key, val in metrics.items():
            logger.info(f"  MLflow Metric -> {key}: {val}")
        for key, val in params.items():
            logger.info(f"  MLflow Param -> {key}: {val}")
        for path in artifact_paths:
            logger.info(f"  MLflow Artifact -> {path}")

    @staticmethod
    def run_evidently_drift_analysis(reference_data: pd.DataFrame, current_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Evidently AI ile veri kayması ve veri kalitesi testi yapar.
        (Arayüz tasarımı - PDF sayfa 6'ya göre Celery görevlerine entegrasyon)
        """
        logger.info("Evidently AI Drift Analizi başlatılıyor...")
        # Basit bir PSI (Population Stability Index) hesabı simülasyonu
        psi_value = 0.28  # Eşik değer 0.25'tir
        
        status = "DRIFT_DETECTED" if psi_value > 0.25 else "NORMAL"
        return {
            'psi': psi_value,
            'status': status,
            'action_required': psi_value > 0.25
        }
