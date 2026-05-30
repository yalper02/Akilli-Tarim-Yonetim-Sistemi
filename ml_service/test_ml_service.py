import time
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# =============================================================================
# 1. DOĞRU DURUM (HAPPY PATH) VE ŞEMA TRAM TESTLERİ
# =============================================================================

def test_predict_irrigation_success():
    """
    POST /api/v1/predict/irrigation endpoint'inin geçerli girdilerle doğru şemada veri dönmesini test eder.
    SLA: < 150 ms
    """
    payload = {
        "temperature": 28.5,
        "humidity": 45.0,
        "soil_moisture": 30.0
    }
    
    start_time = time.time()
    response = client.post("/api/v1/predict/irrigation", json=payload)
    duration_ms = (time.time() - start_time) * 1000
    
    assert response.status_code == 200
    data = response.json()
    assert "decision" in data
    assert "prob" in data
    assert "confidence" in data
    assert data["decision"] in [0, 1]
    assert 0.0 <= data["prob"] <= 1.0
    assert 0.0 <= data["confidence"] <= 100.0
    
    # SLA kontrolü
    assert duration_ms < 150.0, f"SLA asildi: {duration_ms:.2f} ms (> 150 ms)"


def test_predict_yield_success():
    """
    POST /api/v1/predict/yield endpoint'inin test edilmesi.
    SLA: < 300 ms
    """
    payload = {
        "crop_type": "bugday",
        "soil_ph": 6.8,
        "soil_ec": 1.2,
        "irrigation_amount": 100.0,
        "fertilizer_amount": 20.0,
        "forecast_days": 14
    }
    
    start_time = time.time()
    response = client.post("/api/v1/predict/yield", json=payload)
    duration_ms = (time.time() - start_time) * 1000
    
    assert response.status_code == 200
    data = response.json()
    assert "forecast" in data
    assert "lower" in data
    assert "upper" in data
    assert len(data["forecast"]) == 14
    assert data["lower"] <= data["upper"]
    
    # SLA kontrolü
    assert duration_ms < 300.0, f"SLA asildi: {duration_ms:.2f} ms (> 300 ms)"


def test_predict_anomaly_success():
    """
    POST /api/v1/predict/anomaly endpoint'inin test edilmesi.
    SLA: < 100 ms
    """
    payload = {
        "sensor_id": "sensor-temp-01",
        "sensor_type": "temperature",
        "value": 48.2,  # Yüksek değer anomali tetiklemeli
        "timestamp": "2026-05-30T17:00:00Z"
    }
    
    start_time = time.time()
    response = client.post("/api/v1/predict/anomaly", json=payload)
    duration_ms = (time.time() - start_time) * 1000
    
    assert response.status_code == 200
    data = response.json()
    assert "score" in data
    assert "is_anomaly" in data
    assert "severity" in data
    assert data["is_anomaly"] is True
    assert data["severity"] in ["low", "medium", "high"]
    
    # SLA kontrolü
    assert duration_ms < 100.0, f"SLA asildi: {duration_ms:.2f} ms (> 100 ms)"


def test_get_models_health():
    """
    GET /api/v1/models/health endpoint'inin test edilmesi.
    SLA: < 50 ms
    """
    start_time = time.time()
    response = client.get("/api/v1/models/health")
    duration_ms = (time.time() - start_time) * 1000
    
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert "last_retrain" in data
    assert len(data["models"]) > 0
    assert data["models"][0]["model_name"] == "XGBoost Irrigation"
    
    # SLA kontrolü
    assert duration_ms < 50.0, f"SLA asildi: {duration_ms:.2f} ms (> 50 ms)"


# =============================================================================
# 2. HATA VE GEÇERSİZ İSTEK (RFC 7807) TESTLERİ
# =============================================================================

def test_predict_irrigation_validation_error():
    """
    Geçersiz parametrelerle istek atıldığında RFC 7807 formatında 422 hatası alınmasını doğrular.
    """
    # Sıcaklık limiti ge=-10.0, le=55.0 arasındadır. 75.0 geçersizdir.
    payload = {
        "temperature": 75.0,
        "humidity": 45.0,
        "soil_moisture": 30.0
    }
    response = client.post("/api/v1/predict/irrigation", json=payload)
    
    assert response.status_code == 422
    data = response.json()
    assert "type" in data
    assert "title" in data
    assert "status" in data
    assert "detail" in data
    assert "suggestion" in data
    assert data["status"] == 422
    assert "Sıcaklık değeri" in data["detail"] or "temperature" in data["detail"] or "Sema dogrulama hatasi" in data["detail"]


def test_predict_yield_invalid_days():
    """
    Tahmin gün sayısı 7, 14, 30 dışında gönderildiğinde 422 hatası dönmesini doğrular.
    """
    payload = {
        "crop_type": "bugday",
        "soil_ph": 6.8,
        "soil_ec": 1.2,
        "irrigation_amount": 100.0,
        "fertilizer_amount": 20.0,
        "forecast_days": 10  # Geçersiz gün
    }
    response = client.post("/api/v1/predict/yield", json=payload)
    
    assert response.status_code == 422
    data = response.json()
    assert data["status"] == 422
    assert "Tahmin süresi" in data["detail"] or "forecast_days" in data["detail"]


def test_get_batch_not_found():
    """
    Olmayan bir batch job_id sorgulandığında 404 hatasının RFC 7807 olarak dönmesini test eder.
    """
    response = client.get("/api/v1/predict/batch/job-unknown")
    
    assert response.status_code == 404
    data = response.json()
    assert data["status"] == 404
    assert "type" in data
    assert "detail" in data
    assert "job-unknown" in data["detail"]


# =============================================================================
# 3. RATE LIMITING TESTLERİ
# =============================================================================

def test_rate_limiting_triggered():
    """
    Normal kullanıcı için 100 olan rate limitin, kısa sürede aşıldığında 429 hata kodu
    ve RFC 7807 yapısında Too Many Requests mesajı dönmesini doğrular.
    """
    # Test ortamında rate limits limit=5 olarak simüle edilebilir
    # İstek atan IP/istemci bilgisini değiştirerek kontrol edelim
    # Header olmadan 'user' olarak istek atıyoruz
    
    # Çok sayıda istek gönderelim
    limit_reached = False
    for i in range(120):  # 100 limitini aşacak şekilde istek at
        response = client.get("/api/v1/models/health")
        if response.status_code == 429:
            limit_reached = True
            data = response.json()
            assert data["status"] == 429
            assert "Hiz Siniri Asildi" in data["title"]
            assert "too-many-requests" in data["type"]
            break
            
    assert limit_reached, "Hız sınırı uyarısı (429) tetiklenemedi."
