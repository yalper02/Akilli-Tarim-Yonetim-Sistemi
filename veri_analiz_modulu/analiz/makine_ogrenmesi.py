"""
Makine Öğrenmesi Modülü
========================

Bu modül, tarımsal IoT verilerine makine öğrenmesi algoritmalarını
uygulayarak tahmin ve sınıflandırma yapar.

Kullanılan Algoritmalar:
    1. Gözetimli Öğrenme (Supervised Learning):
        - Random Forest Regresyon/Sınıflandırma
        - Gradient Boosting (XGBoost benzeri yaklaşım)
        - Destek Vektör Makineleri (SVM)
        - K-En Yakın Komşu (KNN)
    
    2. Gözetimsiz Öğrenme (Unsupervised Learning):
        - K-Means Kümeleme
        - DBSCAN Kümeleme
    
    3. Model Değerlendirme:
        - Çapraz Doğrulama (Cross Validation)
        - Performans Metrikleri (RMSE, MAE, R², F1-Score)

Kütüphaneler:
    - scikit-learn: ML algoritmaları ve model değerlendirme
    - NumPy/Pandas: Veri işleme
    - joblib: Model kaydetme/yükleme
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
import logging
import json
from datetime import datetime

# Scikit-learn kütüphaneleri
from sklearn.model_selection import (
    train_test_split,
    cross_val_score,
    GridSearchCV,
)
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    r2_score,
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from sklearn.ensemble import (
    RandomForestRegressor,
    RandomForestClassifier,
    GradientBoostingRegressor,
    GradientBoostingClassifier,
)
from sklearn.svm import SVR, SVC
from sklearn.neighbors import KNeighborsRegressor, KNeighborsClassifier
from sklearn.cluster import KMeans, DBSCAN
from sklearn.pipeline import Pipeline
import joblib

logger = logging.getLogger(__name__)


class MakineOgrenmesiModeli:
    """
    Tarımsal veri analizi için makine öğrenmesi modeli.
    
    Bu sınıf, sensör verilerini kullanarak:
        - Sulama ihtiyacı tahmini
        - Verim tahmini
        - Toprak durumu sınıflandırması
        - Hastalık riski tahmini
        - Anomali tespiti
    gibi tarımsal kararları destekleyen modeller oluşturur.
    
    Kullanım Örneği:
        >>> model = MakineOgrenmesiModeli()
        >>> model.veri_hazirla(X, y)
        >>> model.model_egit('random_forest', gorev='regresyon')
        >>> tahmin = model.tahmin_yap(yeni_veri)
    """

    DESTEKLENEN_MODELLER = {
        'regresyon': {
            'random_forest': RandomForestRegressor,
            'gradient_boosting': GradientBoostingRegressor,
            'svm': SVR,
            'knn': KNeighborsRegressor,
        },
        'siniflandirma': {
            'random_forest': RandomForestClassifier,
            'gradient_boosting': GradientBoostingClassifier,
            'svm': SVC,
            'knn': KNeighborsClassifier,
        },
    }

    # Hiperparametre arama uzayları
    PARAMETRE_GRIDLERI = {
        'random_forest': {
            'n_estimators': [50, 100, 200],
            'max_depth': [5, 10, 20, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4],
        },
        'gradient_boosting': {
            'n_estimators': [50, 100, 200],
            'learning_rate': [0.01, 0.1, 0.2],
            'max_depth': [3, 5, 7],
            'subsample': [0.8, 0.9, 1.0],
        },
        'svm': {
            'C': [0.1, 1, 10],
            'kernel': ['rbf', 'linear', 'poly'],
            'gamma': ['scale', 'auto'],
        },
        'knn': {
            'n_neighbors': [3, 5, 7, 11],
            'weights': ['uniform', 'distance'],
            'metric': ['euclidean', 'manhattan'],
        },
    }

    def __init__(self):
        """Makine Öğrenmesi modelini başlatır."""
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.ozellik_adlari: List[str] = []
        self.gorev: Optional[str] = None
        self.model_adi: Optional[str] = None
        self.egitim_metrikleri: Dict = {}
        self.X_egitim = None
        self.X_test = None
        self.y_egitim = None
        self.y_test = None

    # =========================================================================
    # 1. VERİ HAZIRLAMA
    # =========================================================================

    def veri_hazirla(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        test_orani: float = 0.2,
        olcekle: bool = True,
        random_state: int = 42
    ) -> Dict[str, Any]:
        """
        Model eğitimi için veriyi hazırlar.
        
        Adımlar:
            1. Eğitim/test ayrımı
            2. Özellik ölçeklendirme (StandardScaler)
            3. Kategorik değişken kodlama
        
        Args:
            X: Özellik matrisi (bağımsız değişkenler)
            y: Hedef değişken
            test_orani: Test setinin oranı (varsayılan: %20)
            olcekle: Özellik ölçeklendirme yapılsın mı?
            random_state: Rastgelelik tohumu
            
        Returns:
            Veri hazırlama özet bilgileri
        """
        self.ozellik_adlari = list(X.columns)

        # Eğitim/test ayrımı
        self.X_egitim, self.X_test, self.y_egitim, self.y_test = \
            train_test_split(X, y, test_size=test_orani, random_state=random_state)

        # Ölçeklendirme
        if olcekle:
            self.X_egitim = pd.DataFrame(
                self.scaler.fit_transform(self.X_egitim),
                columns=self.ozellik_adlari,
                index=self.X_egitim.index
            )
            self.X_test = pd.DataFrame(
                self.scaler.transform(self.X_test),
                columns=self.ozellik_adlari,
                index=self.X_test.index
            )

        bilgi = {
            'toplam_veri': len(X),
            'egitim_seti_boyutu': len(self.X_egitim),
            'test_seti_boyutu': len(self.X_test),
            'ozellik_sayisi': len(self.ozellik_adlari),
            'ozellikler': self.ozellik_adlari,
            'olceklendirme': olcekle,
        }

        logger.info(f"Veri hazırlandı: {bilgi}")
        return bilgi

    # =========================================================================
    # 2. MODEL EĞİTME
    # =========================================================================

    def model_egit(
        self,
        model_adi: str = 'random_forest',
        gorev: str = 'regresyon',
        hiperparametre_arama: bool = False,
        **model_parametreleri
    ) -> Dict[str, Any]:
        """
        Belirtilen ML modelini eğitir.
        
        Desteklenen Modeller:
            - random_forest: Çoklu karar ağaçlarının birleşimi.
              Tarımsal verilerde yüksek performans gösterir.
            - gradient_boosting: Sıralı öğrenme ile hata düzeltme.
              Karmaşık ilişkileri modellemede etkilidir.
            - svm: Destek Vektör Makineleri. 
              Küçük veri setlerinde güçlüdür.
            - knn: K-En Yakın Komşu.
              Basit ama etkili, parametre seçimi kritik.
        
        Args:
            model_adi: Kullanılacak model ('random_forest', 'gradient_boosting', 'svm', 'knn')
            gorev: Görev tipi ('regresyon' veya 'siniflandirma')
            hiperparametre_arama: GridSearchCV ile hiperparametre optimizasyonu
            **model_parametreleri: Modele özel ek parametreler
            
        Returns:
            Eğitim sonuç metrikleri
        """
        if self.X_egitim is None:
            raise ValueError("Önce veri_hazirla() metodunu çağırın.")

        self.gorev = gorev
        self.model_adi = model_adi

        # Model sınıfını seç
        model_sinifi = self.DESTEKLENEN_MODELLER[gorev][model_adi]

        if hiperparametre_arama:
            # Grid Search ile en iyi parametreleri bul
            parametre_grid = self.PARAMETRE_GRIDLERI.get(model_adi, {})
            grid_arama = GridSearchCV(
                model_sinifi(),
                parametre_grid,
                cv=5,
                scoring='neg_mean_squared_error' if gorev == 'regresyon' else 'accuracy',
                n_jobs=-1,
                verbose=0
            )
            grid_arama.fit(self.X_egitim, self.y_egitim)
            self.model = grid_arama.best_estimator_
            en_iyi_parametreler = grid_arama.best_params_
            logger.info(f"En iyi parametreler: {en_iyi_parametreler}")
        else:
            self.model = model_sinifi(**model_parametreleri)
            self.model.fit(self.X_egitim, self.y_egitim)
            en_iyi_parametreler = model_parametreleri

        # Model performansını değerlendir
        self.egitim_metrikleri = self._model_degerlendir()
        self.egitim_metrikleri['model_adi'] = model_adi
        self.egitim_metrikleri['gorev'] = gorev
        self.egitim_metrikleri['parametreler'] = en_iyi_parametreler

        logger.info(f"Model eğitildi: {model_adi} ({gorev})")
        return self.egitim_metrikleri

    def _model_degerlendir(self) -> Dict[str, Any]:
        """Model performans metriklerini hesaplar."""
        y_tahmin = self.model.predict(self.X_test)
        metrikler = {}

        if self.gorev == 'regresyon':
            metrikler = {
                'rmse': float(np.sqrt(mean_squared_error(self.y_test, y_tahmin))),
                'mae': float(mean_absolute_error(self.y_test, y_tahmin)),
                'r2_skoru': float(r2_score(self.y_test, y_tahmin)),
                'aciklanan_varyans_orani': float(
                    r2_score(self.y_test, y_tahmin) * 100
                ),
            }
        elif self.gorev == 'siniflandirma':
            metrikler = {
                'dogruluk': float(accuracy_score(self.y_test, y_tahmin)),
                'siniflandirma_raporu': classification_report(
                    self.y_test, y_tahmin, output_dict=True
                ),
                'karisiklik_matrisi': confusion_matrix(
                    self.y_test, y_tahmin
                ).tolist(),
            }

        # Çapraz doğrulama
        cv_skorlari = cross_val_score(
            self.model, self.X_egitim, self.y_egitim, cv=5,
            scoring='neg_mean_squared_error' if self.gorev == 'regresyon' else 'accuracy'
        )
        metrikler['capraz_dogrulama'] = {
            'ortalama': float(cv_skorlari.mean()),
            'std': float(cv_skorlari.std()),
            'skorlar': cv_skorlari.tolist(),
        }

        return metrikler

    # =========================================================================
    # 3. TAHMİN
    # =========================================================================

    def tahmin_yap(self, X_yeni: pd.DataFrame) -> np.ndarray:
        """
        Eğitilmiş model ile yeni veriler üzerinde tahmin yapar.
        
        Args:
            X_yeni: Tahmin yapılacak yeni özellik matrisi
            
        Returns:
            Tahmin sonuçları dizisi
        """
        if self.model is None:
            raise ValueError("Henüz eğitilmiş bir model yok. model_egit() çağırın.")

        # Ölçeklendirme uygula
        X_olcekli = self.scaler.transform(X_yeni)
        tahminler = self.model.predict(X_olcekli)

        return tahminler

    # =========================================================================
    # 4. ÖZELLİK ÖNEMİ
    # =========================================================================

    def ozellik_onemi(self) -> Dict[str, float]:
        """
        Model özellik önem derecelerini döndürür.
        
        Random Forest ve Gradient Boosting modelleri için
        hangi sensör verisinin tahmin için en önemli olduğunu belirler.
        
        Returns:
            Özellik adı → önem derecesi eşlemesi (azalan sırada)
        """
        if not hasattr(self.model, 'feature_importances_'):
            logger.warning("Bu model özellik önemi desteklemiyor.")
            return {}

        onemler = self.model.feature_importances_
        onem_dict = dict(zip(self.ozellik_adlari, onemler))

        # Azalan sırada sırala
        onem_dict = dict(
            sorted(onem_dict.items(), key=lambda x: x[1], reverse=True)
        )

        return onem_dict

    # =========================================================================
    # 5. KÜMELEME ANALİZİ
    # =========================================================================

    def kumeleme_analizi(
        self,
        X: pd.DataFrame,
        yontem: str = 'kmeans',
        n_kume: int = 3,
        **parametreler
    ) -> Dict[str, Any]:
        """
        Gözetimsiz öğrenme ile veri kümeleme.
        
        Tarımsal uygulamada:
            - Benzer toprak özelliklerine sahip bölgeleri gruplamak
            - Sulama ihtiyacına göre alanları sınıflandırmak
            - Sensör davranış kalıplarını belirlemek
        
        Args:
            X: Kümelenecek veri matrisi
            yontem: Kümeleme yöntemi ('kmeans' veya 'dbscan')
            n_kume: Küme sayısı (sadece K-Means için)
            **parametreler: Ek model parametreleri
            
        Returns:
            Kümeleme sonuçları ve metrikleri
        """
        # Ölçeklendirme
        X_olcekli = self.scaler.fit_transform(X)

        if yontem == 'kmeans':
            model = KMeans(
                n_clusters=n_kume,
                random_state=42,
                n_init=10,
                **parametreler
            )
            etiketler = model.fit_predict(X_olcekli)

            sonuclar = {
                'yontem': 'K-Means',
                'kume_sayisi': n_kume,
                'etiketler': etiketler.tolist(),
                'kume_merkezleri': model.cluster_centers_.tolist(),
                'inertia': float(model.inertia_),
                'kume_dagilimi': {
                    f'Küme {i}': int((etiketler == i).sum())
                    for i in range(n_kume)
                },
            }

        elif yontem == 'dbscan':
            eps = parametreler.get('eps', 0.5)
            min_samples = parametreler.get('min_samples', 5)
            model = DBSCAN(eps=eps, min_samples=min_samples)
            etiketler = model.fit_predict(X_olcekli)

            n_kume_bulunan = len(set(etiketler)) - (1 if -1 in etiketler else 0)
            n_gurultu = int((etiketler == -1).sum())

            sonuclar = {
                'yontem': 'DBSCAN',
                'bulunan_kume_sayisi': n_kume_bulunan,
                'gurultu_noktasi_sayisi': n_gurultu,
                'etiketler': etiketler.tolist(),
                'eps': eps,
                'min_samples': min_samples,
            }
        else:
            raise ValueError(f"Desteklenmeyen kümeleme yöntemi: {yontem}")

        logger.info(f"Kümeleme analizi tamamlandı: {yontem}")
        return sonuclar

    def optimal_kume_sayisi_bul(
        self, X: pd.DataFrame, max_kume: int = 10
    ) -> Dict[str, Any]:
        """
        Elbow (Dirsek) yöntemi ile optimal küme sayısını belirler.
        
        Args:
            X: Kümelenecek veri
            max_kume: Test edilecek maksimum küme sayısı
            
        Returns:
            Her küme sayısı için inertia değerleri
        """
        X_olcekli = self.scaler.fit_transform(X)
        inertia_degerleri = []

        for k in range(2, max_kume + 1):
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(X_olcekli)
            inertia_degerleri.append({
                'kume_sayisi': k,
                'inertia': float(kmeans.inertia_),
            })

        return {
            'sonuclar': inertia_degerleri,
            'aciklama': (
                "Elbow yöntemi: Inertia değerinin keskin bir şekilde "
                "düştüğü noktadaki küme sayısı optimaldir."
            ),
        }

    # =========================================================================
    # 6. MODEL KAYDETME / YÜKLEME
    # =========================================================================

    def modeli_kaydet(self, dosya_yolu: str):
        """
        Eğitilmiş modeli diske kaydeder.
        
        Args:
            dosya_yolu: Kaydedilecek dosya yolu (.joblib)
        """
        kayit_verisi = {
            'model': self.model,
            'scaler': self.scaler,
            'ozellik_adlari': self.ozellik_adlari,
            'gorev': self.gorev,
            'model_adi': self.model_adi,
            'egitim_metrikleri': self.egitim_metrikleri,
            'kayit_zamani': datetime.now().isoformat(),
        }
        joblib.dump(kayit_verisi, dosya_yolu)
        logger.info(f"Model kaydedildi: {dosya_yolu}")

    def modeli_yukle(self, dosya_yolu: str):
        """
        Kaydedilmiş modeli diskten yükler.
        
        Args:
            dosya_yolu: Yüklenecek model dosyası (.joblib)
        """
        kayit_verisi = joblib.load(dosya_yolu)
        self.model = kayit_verisi['model']
        self.scaler = kayit_verisi['scaler']
        self.ozellik_adlari = kayit_verisi['ozellik_adlari']
        self.gorev = kayit_verisi['gorev']
        self.model_adi = kayit_verisi['model_adi']
        self.egitim_metrikleri = kayit_verisi['egitim_metrikleri']
        logger.info(f"Model yüklendi: {dosya_yolu}")


# =============================================================================
# TARIMSAL TAHMİN FONKSİYONLARI
# =============================================================================

def sulama_ihtiyaci_tahmin_modeli(
    sensor_verileri: pd.DataFrame,
    hedef_sutun: str = 'sulama_ihtiyaci'
) -> Dict[str, Any]:
    """
    Sensör verilerinden sulama ihtiyacını tahmin eden model oluşturur.
    
    Kullanılan özellikler:
        - Toprak nemi
        - Hava sıcaklığı
        - Hava nem oranı
        - Rüzgar hızı
        - Son yağış miktarı
    
    Args:
        sensor_verileri: Sensör veri DataFrame'i
        hedef_sutun: Tahmin edilecek hedef sütun
        
    Returns:
        Model eğitim sonuçları ve performans metrikleri
    """
    ozellik_sutunlari = [
        'toprak_nem', 'sicaklik', 'hava_nem',
        'ruzgar_hizi', 'son_yagis'
    ]

    # Mevcut sütunları filtrele
    mevcut_ozellikler = [s for s in ozellik_sutunlari if s in sensor_verileri.columns]

    X = sensor_verileri[mevcut_ozellikler]
    y = sensor_verileri[hedef_sutun]

    model = MakineOgrenmesiModeli()
    model.veri_hazirla(X, y)

    # En iyi modeli bulmak için farklı modelleri dene
    sonuclar = {}
    for model_adi in ['random_forest', 'gradient_boosting']:
        metrikler = model.model_egit(model_adi=model_adi, gorev='regresyon')
        sonuclar[model_adi] = metrikler

    # En iyi modeli seç (en düşük RMSE)
    en_iyi = min(sonuclar.items(), key=lambda x: x[1]['rmse'])

    return {
        'en_iyi_model': en_iyi[0],
        'tum_sonuclar': sonuclar,
        'ozellik_onemleri': model.ozellik_onemi(),
    }


def verim_tahmin_modeli(
    tarla_verileri: pd.DataFrame,
    hedef: str = 'verim'
) -> Dict[str, Any]:
    """
    Tarla verilerinden ürün verimini tahmin eden model.
    
    Faktörler:
        - Toprak kalitesi (pH, EC, nem)
        - İklim verileri (sıcaklık, yağış, güneşlenme)
        - Tarımsal müdahaleler (sulama, gübreleme)
    
    Args:
        tarla_verileri: Tarla veri DataFrame'i
        hedef: Hedef değişken sütun adı
        
    Returns:
        Verim tahmin modeli sonuçları
    """
    model = MakineOgrenmesiModeli()

    ozellikler = tarla_verileri.drop(columns=[hedef])
    y = tarla_verileri[hedef]

    model.veri_hazirla(ozellikler, y)

    # Gradient Boosting genellikle tarımsal verim tahmininde iyi sonuç verir
    metrikler = model.model_egit(
        model_adi='gradient_boosting',
        gorev='regresyon',
        hiperparametre_arama=True
    )

    return {
        'metrikler': metrikler,
        'ozellik_onemleri': model.ozellik_onemi(),
        'model_nesnesi': model,
    }
