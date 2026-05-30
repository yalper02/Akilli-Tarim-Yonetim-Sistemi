from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any, Optional

# =============================================================================
# 1. SULAMA TAHMİNİ ŞEMALARI (POST /api/v1/predict/irrigation)
# =============================================================================

class IrrigationRequest(BaseModel):
    temperature: float = Field(..., description="Hava sıcaklığı (Celsius)", ge=-10.0, le=55.0)
    humidity: float = Field(..., description="Hava bağıl nem oranı (%)", ge=0.0, le=100.0)
    soil_moisture: float = Field(..., description="Toprak nem oranı (%)", ge=0.0, le=100.0)

    @field_validator('temperature')
    def validate_temp(cls, v):
        if v < -10.0 or v > 55.0:
            raise ValueError("Sıcaklık değeri -10 ile 55 derece arasında olmalıdır.")
        return v


class IrrigationResponse(BaseModel):
    decision: int = Field(..., description="Sulama kararı (0: Sula, 1: Sulamayı Durdur)", ge=0, le=1)
    prob: float = Field(..., description="Sulama gereksinimi olasılığı", ge=0.0, le=1.0)
    confidence: float = Field(..., description="Model tahmin güven düzeyi (%)", ge=0.0, le=100.0)


# =============================================================================
# 2. MAHSUL VERİM TAHMİNİ ŞEMALARI (POST /api/v1/predict/yield)
# =============================================================================

class YieldRequest(BaseModel):
    crop_type: str = Field(..., description="Ürün türü (örn: bugday, misir, pamuk)")
    soil_ph: float = Field(..., description="Toprak pH derecesi", ge=0.0, le=14.0)
    soil_ec: float = Field(..., description="Toprak elektriksel iletkenliği (EC)", ge=0.0)
    irrigation_amount: float = Field(..., description="Planlanan sulama miktarı (m³/dekar)", ge=0.0)
    fertilizer_amount: float = Field(..., description="Planlanan gübre miktarı (kg/dekar)", ge=0.0)
    forecast_days: int = Field(..., description="Tahmin gün sayısı (7, 14 veya 30 gün)")

    @field_validator('forecast_days')
    def validate_days(cls, v):
        if v not in [7, 14, 30]:
            raise ValueError("Tahmin süresi sadece 7, 14 veya 30 gün olabilir.")
        return v


class YieldResponse(BaseModel):
    forecast: List[float] = Field(..., description="Günlük tahmini ürün verimi listesi (kg/dekar)")
    lower: float = Field(..., description="Verim tahmini alt güven sınırı")
    upper: float = Field(..., description="Verim tahmini üst güven sınırı")


# =============================================================================
# 3. ANOMALİ TESPİTİ ŞEMALARI (POST /api/v1/predict/anomaly)
# =============================================================================

class AnomalyRequest(BaseModel):
    sensor_id: str = Field(..., description="Sensör benzersiz kimliği (ID)")
    sensor_type: str = Field(..., description="Sensör türü (temperature, humidity, soil_moisture, etc.)")
    value: float = Field(..., description="Sensör okuma değeri")
    timestamp: str = Field(..., description="Okuma zaman damgası (ISO-8601)")

    @field_validator('sensor_type')
    def validate_sensor_type(cls, v):
        allowed = ['temperature', 'humidity', 'soil_moisture', 'ph', 'ec']
        if v.lower() not in allowed:
            raise ValueError(f"Desteklenmeyen sensör tipi. Şunlardan biri olmalıdır: {allowed}")
        return v.lower()


class AnomalyResponse(BaseModel):
    score: float = Field(..., description="Hesaplanan anomali skoru", ge=0.0, le=1.0)
    is_anomaly: bool = Field(..., description="Anomali kararı (True/False)")
    severity: str = Field(..., description="Anomali derecesi (none, low, medium, high)")


# =============================================================================
# 4. TOPLU TAHMİN SORGULAMA ŞEMASI (GET /api/v1/predict/batch/{job_id})
# =============================================================================

class BatchStatusResponse(BaseModel):
    status: str = Field(..., description="Toplu tahmin görevinin durumu (pending, running, completed, failed)")
    results: List[Any] = Field(..., description="Tahmin sonuçları listesi")
    meta: Dict[str, Any] = Field(..., description="Ek metadata bilgileri (örn: baslangic_zamani, islenen_kayit)")


# =============================================================================
# 5. MODEL SAĞLIK VE DURUM ŞEMASI (GET /api/v1/models/health)
# =============================================================================

class ModelInfo(BaseModel):
    model_name: str = Field(..., description="Modelin adı")
    version: str = Field(..., description="MLflow kayıt sürümü")
    accuracy: float = Field(..., description="Validasyon F1/R2 skoru")
    status: str = Field(..., description="Model durumu (active, maintenance)")


class ModelHealthResponse(BaseModel):
    models: List[ModelInfo] = Field(..., description="Kayıtlı ve aktif modellerin listesi")
    last_retrain: str = Field(..., description="En son otomatik model yeniden eğitilme zamanı")


# =============================================================================
# 6. KULLANICI GERİBİLDİRİM ŞEMALARI (POST /api/v1/feedback)
# =============================================================================

class FeedbackRequest(BaseModel):
    prediction_id: str = Field(..., description="Geribildirim yapılacak tahminin ID'si")
    actual_output: int = Field(..., description="Kullanıcı tarafından gözlenen gerçek değer/sınıf (0 veya 1)")
    is_correct: bool = Field(..., description="Tahminin doğruluğu")

    @field_validator('actual_output')
    def validate_actual(cls, v):
        if v not in [0, 1]:
            raise ValueError("Gözlenen çıktı sadece 0 veya 1 olabilir.")
        return v


class FeedbackResponse(BaseModel):
    accepted: bool = Field(..., description="Geribildirimin başarıyla işlenip kaydedildiğini belirtir")
    drift_score: float = Field(..., description="Geribildirim sonrası hesaplanan güncel veri drift skoru")


# =============================================================================
# 7. RFC 7807 HATA YÖNETİM ŞEMASI
# =============================================================================

class RFC7807ProblemDetails(BaseModel):
    type: str = Field(..., description="Hata türünü tanımlayan URI")
    title: str = Field(..., description="Hatanın kısa açıklaması")
    status: int = Field(..., description="HTTP durum kodu")
    detail: str = Field(..., description="Hatanın detaylı açıklaması")
    instance: Optional[str] = Field(None, description="Hatanın oluştuğu endpoint adresi")
    suggestion: Optional[str] = Field(None, description="Çözüm önerisi")
