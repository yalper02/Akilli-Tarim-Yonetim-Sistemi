import logging
import httpx
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

# Django and DRF imports (Mocked/Simulated since Django configuration is minimal or on other branches)
try:
    from rest_framework.views import APIView
    from rest_framework.response import Response
    from rest_framework import status as drf_status
    from celery import shared_task
except ImportError:
    # Dummy fallbacks for running standalone or outside full Django runtime environment
    class APIView:
        pass
    class Response:
        def __init__(self, data=None, status=200):
            self.data = data
            self.status = status
    class drf_status:
        HTTP_200_OK = 200
        HTTP_400_BAD_REQUEST = 400
        HTTP_500_INTERNAL_SERVER_ERROR = 500
    def shared_task(func):
        return func

logger = logging.getLogger("DjangoMLEntegrasyon")

# =============================================================================
# 1. ML SERVICE REST CLIENT (HTTPX ASYNC)
# =============================================================================

class MLServiceClient:
    """
    FastAPI ML Mikro-servisine asenkron HTTP istekleri gönderen entegrasyon istemcisi.
    """
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.timeout = 10.0  # saniye

    async def get_headers(self, client_type: str = "django_backend") -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "X-Client-Type": client_type
        }

    async def predict_irrigation(self, temperature: float, humidity: float, soil_moisture: float) -> Dict[str, Any]:
        """
        Sensör verilerini gönderip sulama tahmini kararını alır.
        """
        url = f"{self.base_url}/api/v1/predict/irrigation"
        payload = {
            "temperature": temperature,
            "humidity": humidity,
            "soil_moisture": soil_moisture
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            headers = await self.get_headers("sensor_gateway")
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()

    async def predict_yield(
        self,
        crop_type: str,
        soil_ph: float,
        soil_ec: float,
        irrigation_amount: float,
        fertilizer_amount: float,
        forecast_days: int
    ) -> Dict[str, Any]:
        """
        Arazi girdilerine göre mahsul verim tahmini alır.
        """
        url = f"{self.base_url}/api/v1/predict/yield"
        payload = {
            "crop_type": crop_type,
            "soil_ph": soil_ph,
            "soil_ec": soil_ec,
            "irrigation_amount": irrigation_amount,
            "fertilizer_amount": fertilizer_amount,
            "forecast_days": forecast_days
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            headers = await self.get_headers("django_backend")
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()

    async def predict_anomaly(self, sensor_id: str, sensor_type: str, value: float) -> Dict[str, Any]:
        """
        Sensör okuma değerine göre anomali kontrolü yapar.
        """
        url = f"{self.base_url}/api/v1/predict/anomaly"
        payload = {
            "sensor_id": sensor_id,
            "sensor_type": sensor_type,
            "value": value,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            headers = await self.get_headers("sensor_gateway")
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()

    async def get_models_health(self) -> Dict[str, Any]:
        """
        Modellerin kayıt durumu ve sağlık durumlarını çeker.
        """
        url = f"{self.base_url}/api/v1/models/health"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            headers = await self.get_headers("django_backend")
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()

    async def send_feedback(self, prediction_id: str, actual_output: int, is_correct: bool) -> Dict[str, Any]:
        """
        Model tahmin doğrulaması için geribildirim gönderir.
        """
        url = f"{self.base_url}/api/v1/feedback"
        payload = {
            "prediction_id": prediction_id,
            "actual_output": actual_output,
            "is_correct": is_correct
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            headers = await self.get_headers("django_backend")
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()


# =============================================================================
# 2. CELERY TOPLU TAHMİN GÖREVİ (BATCH PREDICTION)
# =============================================================================

@shared_task
def run_daily_batch_prediction():
    """
    Her gece 02:00'de Celery Beat tarafından tetiklenen toplu verim tahmini görevi.
    Verileri veri tabanından çeker, ML servisini çağırır ve TimescaleDB hypertable'ına yazar.
    """
    logger.info("Celery Toplu Tahmin Görevi Başlatıldı: Gece 02:00 Rutini...")
    
    # 1. Simüle Edilmiş Veritabanından Tarla/Arazi Verilerinin Çekilmesi
    # Normalde: parceller = Parcel.objects.filter(is_active=True)
    parceller = [
        {"id": 1, "crop_type": "bugday", "soil_ph": 6.8, "soil_ec": 1.2, "irrigation_amount": 150.0, "fertilizer_amount": 25.0},
        {"id": 2, "crop_type": "misir", "soil_ph": 6.2, "soil_ec": 1.8, "irrigation_amount": 220.0, "fertilizer_amount": 35.0},
        {"id": 3, "crop_type": "pamuk", "soil_ph": 7.1, "soil_ec": 1.5, "irrigation_amount": 180.0, "fertilizer_amount": 30.0}
    ]
    
    client = MLServiceClient()
    predictions_to_save = []
    
    async def process_batch():
        for parcel in parceller:
            try:
                # 30 günlük verim projeksiyonu sorgula
                res = await client.predict_yield(
                    crop_type=parcel["crop_type"],
                    soil_ph=parcel["soil_ph"],
                    soil_ec=parcel["soil_ec"],
                    irrigation_amount=parcel["irrigation_amount"],
                    fertilizer_amount=parcel["fertilizer_amount"],
                    forecast_days=30
                )
                
                predictions_to_save.append({
                    "parcel_id": parcel["id"],
                    "forecast": res["forecast"],
                    "lower_ci": res["lower"],
                    "upper_ci": res["upper"],
                    "timestamp": datetime.utcnow()
                })
                logger.info(f"Tarla {parcel['id']} için tahmin başarıyla alındı. Son gün tahmini: {res['forecast'][-1]} kg/dekar")
            except Exception as e:
                logger.error(f"Tarla {parcel['id']} için tahmin alınırken hata oluştu: {str(e)}")
                
    # Asenkron HTTP isteklerini çalıştır
    asyncio.run(process_batch())
    
    # 2. TimescaleDB Hypertable Simüle Kaydı
    # Normalde: SQLAlchemy ORM veya psycopg2 ile hypertable'a bulk insert
    if predictions_to_save:
        logger.info(f"TimescaleDB Hypertable'a {len(predictions_to_save)} tahmin kaydı bulk insert ediliyor...")
        # Simüle edilen işlem başarılı
        logger.info("Kaydetme işlemi başarıyla tamamlandı (TimescaleDB hypertable aggregation views güncellendi).")
    else:
        logger.warning("Kaydedilecek tahmin bulunamadı.")
        
    return len(predictions_to_save)


# =============================================================================
# 3. DJANGO REST FRAMEWORK (DRF) KÖPRÜ VIEW'LARI
# =============================================================================

class DRFIrrigationPredictionView(APIView):
    """
    Mobil Uygulama/Dashboard için REST API Köprüsü.
    İstekleri alır, ML mikro-servisine asenkron olarak iletir ve yanıtı döner.
    """
    def post(self, request, *args, **kwargs):
        # İstek gövdesinden verileri al
        temp = request.data.get("temperature")
        hum = request.data.get("humidity")
        soil = request.data.get("soil_moisture")
        
        if temp is None or hum is None or soil is None:
            return Response(
                {"error": "Eksik parametre. temperature, humidity ve soil_moisture zorunludur."},
                status=drf_status.HTTP_400_BAD_REQUEST
            )
            
        client = MLServiceClient()
        
        # Asenkron çağrıyı çalıştır
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                client.predict_irrigation(float(temp), float(hum), float(soil))
            )
            loop.close()
            return Response(result, status=drf_status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"ML Servisine bağlanırken hata oluştu: {str(e)}")
            return Response(
                {
                    "type": "https://atys.tarim.gov.tr/probs/gateway-error",
                    "title": "ML Servis Baglanti Hatasi",
                    "status": 502,
                    "detail": f"FastAPI ML servisi ile haberlesilemedi: {str(e)}"
                },
                status=drf_status.HTTP_500_INTERNAL_SERVER_ERROR
            )
