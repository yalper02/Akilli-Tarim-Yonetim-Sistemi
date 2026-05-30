import time
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from schemas import (
    IrrigationRequest, IrrigationResponse,
    YieldRequest, YieldResponse,
    AnomalyRequest, AnomalyResponse,
    BatchStatusResponse, ModelHealthResponse,
    FeedbackRequest, FeedbackResponse,
    RFC7807ProblemDetails, ModelInfo
)

# Logging Konfigürasyonu
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MLMicroservice")

app = FastAPI(
    title="ATYS ML Microservice API",
    description="Akıllı Tarım Yönetim Sistemi Makine Öğrenmesi Modelleri API Servisi",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# 1. RATE LIMITING VE SLA İZLEME MIDDLEWARE
# =============================================================================

# Basit In-Memory Hız Sınırlandırıcı (Rate Limiting) Takibi
# Gerçek sistemde Redis ile yapılır.
rate_limit_store: Dict[str, List[float]] = {}

def check_rate_limit(client_id: str, limit: int, period: float = 60.0):
    """
    Belirli bir istemci (client_id) için hız sınırını kontrol eder.
    Limit aşıldığında HTTPException fırlatır.
    """
    now = time.time()
    if client_id not in rate_limit_store:
        rate_limit_store[client_id] = []
        
    # Periyod dışı eski istekleri temizle
    rate_limit_store[client_id] = [t for t in rate_limit_store[client_id] if now - t < period]
    
    if len(rate_limit_store[client_id]) >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Istek hiz siniri asildi. Limit: {limit} req/{period}sn."
        )
        
    rate_limit_store[client_id].append(now)


@app.middleware("http")
async def sla_and_rate_limit_middleware(request: Request, call_next):
    """
    1. İstemci tipine göre Rate Limiting uygular.
    2. SLA süresini (yanıt süresini) ölçer ve loglar.
    """
    # 1. Rate Limiting Kontrolü
    # İstemci tipini header'dan oku (Simüle edilmiş Gateway vs User)
    client_type = request.headers.get("X-Client-Type", "user")
    client_ip = request.client.host if request.client else "unknown"
    client_key = f"{client_type}:{client_ip}"
    
    try:
        # Sensör gateway: 1000 req/dk | Normal kullanıcı: 100 req/dk
        if client_type == "sensor_gateway":
            check_rate_limit(client_key, limit=1000, period=60.0)
        else:
            check_rate_limit(client_key, limit=100, period=60.0)
    except HTTPException as ex:
        # RFC 7807 formatında rate limit hatası dön
        problem = RFC7807ProblemDetails(
            type="https://atys.tarim.gov.tr/probs/too-many-requests",
            title="Hiz Siniri Asildi (Rate Limit Exceeded)",
            status=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=ex.detail,
            instance=request.url.path,
            suggestion="Lutfen istek sikligini azaltin veya sensör gateway header'ini dogrulayin."
        )
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content=problem.model_dump()
        )
        
    # 2. SLA Yanıt Süresi Ölçümü
    start_time = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start_time) * 1000
    
    logger.info(f"Endpoint: {request.url.path} | Client: {client_type} | SLA Latency: {duration_ms:.2f} ms")
    
    # SLA sürelerini response header'ına ekle
    response.headers["X-SLA-Duration-MS"] = f"{duration_ms:.2f}"
    
    return response


# =============================================================================
# 2. HATA YÖNETİMİ (RFC 7807 PROBLEM DETAILS)
# =============================================================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Pydantic şema doğrulaması hatalarını yakalar ve RFC 7807 formatında döner.
    """
    errors = exc.errors()
    # İlk hatayı detaylandır
    detail_msg = "Sema dogrulama hatasi: "
    if errors:
        loc = " -> ".join(str(l) for l in errors[0]['loc'])
        msg = errors[0]['msg']
        detail_msg += f"[{loc}] {msg}"
        
    problem = RFC7807ProblemDetails(
        type="https://atys.tarim.gov.tr/probs/validation-error",
        title="Gecersiz Istek Semasi (Validation Error)",
        status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=detail_msg,
        instance=request.url.path,
        suggestion="Lutfen Pydantic semasina uygun parametreler gönderdiginizden emin olun."
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=problem.model_dump()
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    HTTPException hatalarını yakalar ve RFC 7807 formatında döner.
    """
    problem = RFC7807ProblemDetails(
        type=f"https://atys.tarim.gov.tr/probs/http-error-{exc.status_code}",
        title="HTTP Istek Hatasi",
        status=exc.status_code,
        detail=exc.detail,
        instance=request.url.path,
        suggestion="Istegi ve parametreleri kontrol ederek tekrar deneyin."
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=problem.model_dump()
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Bilinmeyen tüm hataları yakalar ve 500 koduyla RFC 7807 formatında döner.
    """
    logger.error(f"Sistem Hatası: {str(exc)}", exc_info=True)
    problem = RFC7807ProblemDetails(
        type="https://atys.tarim.gov.tr/probs/internal-server-error",
        title="Sistem Hatasi (Internal Server Error)",
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Sunucuda beklenmeyen bir hata olustu. Hata loglari inceleniyor.",
        instance=request.url.path,
        suggestion="Sistem yöneticinizle iletisime gecin veya daha sonra tekrar deneyin."
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=problem.model_dump()
    )


# =============================================================================
# 3. MOCK VERİ TABANI VE TAHMİN MOTORLARI
# =============================================================================

# Simüle edilmiş toplu iş (batch prediction job) veritabanı
batch_jobs: Dict[str, Dict[str, Any]] = {
    "job-101": {
        "status": "completed",
        "results": [
            {"tarla_id": 1, "decision": 0, "prob": 0.88},
            {"tarla_id": 2, "decision": 1, "prob": 0.12},
            {"tarla_id": 3, "decision": 0, "prob": 0.94}
        ],
        "meta": {"baslangic_zamani": "2026-05-30T02:00:00Z", "islenen_kayit": 3}
    },
    "job-102": {
        "status": "running",
        "results": [],
        "meta": {"baslangic_zamani": "2026-05-30T16:45:00Z", "islenen_kayit": 150}
    }
}


# =============================================================================
# 4. REST API ENDPOINT TANIMLAMALARI
# =============================================================================

@app.post(
    "/api/v1/predict/irrigation",
    response_model=IrrigationResponse,
    summary="Sulama Kararı Tahmini",
    response_description="Sensör verilerine göre sulama kararını döner."
)
async def predict_irrigation(request: IrrigationRequest):
    """
    Toprak nemi, hava sıcaklığı ve hava nemine göre sulama kararı verir.
    - Toprak nemi < 35 ve sıcaklık > 25 ise sulama kararı verilir.
    - SLA hedefi: < 150 ms
    """
    # Tahmin hesaplama simülasyonu
    soil_moist = request.soil_moisture
    temp = request.temperature
    hum = request.humidity
    
    # Tahmin mantığı
    if soil_moist < 35.0:
        decision = 0  # Sula
        prob = float(0.5 + (35.0 - soil_moist) / 70.0)  # Nem düştükçe olasılık artar
    else:
        decision = 1  # Sulama
        prob = float((100.0 - soil_moist) / 130.0)
        
    # Sınırları koru
    prob = min(max(prob, 0.02), 0.98)
    confidence = float(85.0 + (temp / 10.0))  # Sıcaklık arttıkça güven artar (basit simülasyon)
    confidence = min(confidence, 99.5)
    
    # SLA gecikme simülasyonu (30-60 ms arası)
    # 150 ms limitini geçmediğinden emin olalım
    time.sleep(0.045)
    
    return IrrigationResponse(
        decision=decision,
        prob=prob,
        confidence=confidence
    )


@app.post(
    "/api/v1/predict/yield",
    response_model=YieldResponse,
    summary="Mahsul Verim Tahmini",
    response_description="Ürün, toprak ve sulama verilerine göre verim tahmini yapar."
)
async def predict_yield(request: YieldRequest):
    """
    Arazi ve iklim verilerine dayanarak 7, 14 veya 30 günlük verim projeksiyonu yapar.
    - SLA hedefi: < 300 ms
    """
    days = request.forecast_days
    crop = request.crop_type.lower()
    
    # Baz verim katsayıları
    base_yield = 250.0
    if "bugday" in crop:
        base_yield = 320.0
    elif "misir" in crop:
        base_yield = 450.0
    elif "pamuk" in crop:
        base_yield = 380.0
        
    # Toprak kalitesi ve gübre etkileri
    ph_factor = 1.0 - abs(request.soil_ph - 6.5) * 0.1  # Optimal pH 6.5
    ph_factor = max(ph_factor, 0.5)
    
    water_fertilizer_bonus = (request.irrigation_amount * 0.2) + (request.fertilizer_amount * 0.5)
    water_fertilizer_bonus = min(water_fertilizer_bonus, 150.0) # tavan
    
    daily_yield = base_yield * ph_factor + water_fertilizer_bonus
    
    # Günlük artış trendi simülasyonu
    forecast = []
    current_yield = daily_yield
    for i in range(days):
        # Her gün hafif büyüme/dalgalanma ekle
        current_yield += float(1.2 + (0.5 - (i % 3) * 0.4))
        forecast.append(round(current_yield, 2))
        
    # Güven aralıkları tahmini (bootstrap simülasyonu)
    std_dev = daily_yield * 0.08
    lower = round(forecast[-1] - 1.96 * std_dev, 2)
    upper = round(forecast[-1] + 1.96 * std_dev, 2)
    
    # SLA gecikme simülasyonu (70-110 ms arası)
    # 300 ms limitini geçmez
    time.sleep(0.09)
    
    return YieldResponse(
        forecast=forecast,
        lower=lower,
        upper=upper
    )


@app.post(
    "/api/v1/predict/anomaly",
    response_model=AnomalyResponse,
    summary="Sensör Anomali Tespiti",
    response_description="Sensör okumalarında anomali derecesini ve kararını döner."
)
async def predict_anomaly(request: AnomalyRequest):
    """
    Okunan sensör değerinin mantıksal sınırların dışında olup olmadığını doğrular.
    - SLA hedefi: < 100 ms
    """
    val = request.value
    stype = request.sensor_type
    
    score = 0.05
    is_anomaly = False
    severity = "none"
    
    # Anomali mantığı kontrolü
    if stype == "temperature":
        if val < 5.0 or val > 45.0:
            is_anomaly = True
            score = float(0.6 + abs(val - 30.0) / 40.0)
        elif val < 0.0 or val > 50.0:
            is_anomaly = True
            score = 0.95
    elif stype == "humidity":
        if val < 10.0 or val > 95.0:
            is_anomaly = True
            score = float(0.7 + (100.0 - val) / 200.0 if val > 95 else 0.7 + (10 - val)/20.0)
    elif stype == "soil_moisture":
        if val < 5.0 or val > 95.0:
            is_anomaly = True
            score = 0.88
            
    score = min(max(score, 0.01), 0.99)
    
    if is_anomaly:
        if score > 0.85:
            severity = "high"
        elif score > 0.60:
            severity = "medium"
        else:
            severity = "low"
            
    # SLA gecikme simülasyonu (25-45 ms arası)
    # 100 ms limitini geçmez
    time.sleep(0.035)
    
    return AnomalyResponse(
        score=score,
        is_anomaly=is_anomaly,
        severity=severity
    )


@app.get(
    "/api/v1/predict/batch/{job_id}",
    response_model=BatchStatusResponse,
    summary="Toplu Tahmin Durumu",
    response_description="Belirtilen toplu tahmin görevinin durumunu sorgular."
)
async def get_batch_status(job_id: str):
    """
    Celery tarafından yürütülen toplu iş durumunu döner.
    - SLA hedefi: < 200 ms
    """
    if job_id not in batch_jobs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Belirtilen batch gorevi bulunamadi: {job_id}"
        )
        
    # SLA gecikme simülasyonu (20-40 ms)
    time.sleep(0.03)
    
    job_info = batch_jobs[job_id]
    return BatchStatusResponse(
        status=job_info["status"],
        results=job_info["results"],
        meta=job_info["meta"]
    )


@app.get(
    "/api/v1/models/health",
    response_model=ModelHealthResponse,
    summary="Modellerin Sağlık Durumu",
    response_description="Aktif ML modellerinin sürümlerini ve doğruluk skorlarını listeler."
)
async def get_models_health():
    """
    MLflow Model Registry'den model sağlık durumlarını çeker.
    - SLA hedefi: < 50 ms
    """
    # SLA gecikme simülasyonu (10-25 ms)
    time.sleep(0.015)
    
    models = [
        ModelInfo(model_name="XGBoost Irrigation", version="1.2.4", accuracy=0.893, status="active"),
        ModelInfo(model_name="Prophet Yield", version="2.1.0", accuracy=0.871, status="active"),
        ModelInfo(model_name="Random Forest Water", version="1.0.1", accuracy=0.856, status="active"),
        ModelInfo(model_name="LSTM Long Term", version="1.1.0", accuracy=0.743, status="maintenance"),
        ModelInfo(model_name="Isolation Forest Anomaly", version="1.0.0", accuracy=0.812, status="active"),
        ModelInfo(model_name="SVM Disease", version="1.0.0", accuracy=0.778, status="maintenance")
    ]
    
    return ModelHealthResponse(
        models=models,
        last_retrain="2026-05-28T04:30:12Z"
    )


@app.post(
    "/api/v1/feedback",
    response_model=FeedbackResponse,
    summary="Kullanıcı Geribildirimi (Online Learning)",
    response_description="Model performans doğrulaması için geribildirim alır."
)
async def post_feedback(request: FeedbackRequest):
    """
    Kullanıcıların model tahminlerine yaptığı düzeltmeleri kaydeder.
    Eğer drift skoru > 0.25 ise otomatik yeniden eğitim tetiklenebilir.
    - SLA hedefi: < 100 ms
    """
    # Geribildirim kaydı simülasyonu
    prediction_id = request.prediction_id
    is_correct = request.is_correct
    
    # Rastgele bir veri drift skoru üret
    # Eğer is_correct False ise drift skoru hafif yükselir
    if not is_correct:
        drift_score = 0.28  # PSI limit aşımı tetikler (> 0.25)
    else:
        drift_score = 0.12
        
    # SLA gecikme simülasyonu (30-50 ms)
    time.sleep(0.04)
    
    return FeedbackResponse(
        accepted=True,
        drift_score=drift_score
    )
