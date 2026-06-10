from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST, require_GET
from django.utils.translation import gettext as _
from django.contrib.auth.models import User
import json
import requests
import random
from datetime import timedelta
from django.utils import timezone
from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.lib.pagesizes import letter
from .models import SensorData, ActivityLog, SystemState, Parcel

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')

def check_rain_probability():
    try:
        res = requests.get('https://api.open-meteo.com/v1/forecast?latitude=38.6748&longitude=39.2225&hourly=precipitation_probability&forecast_hours=12', timeout=3)
        probs = res.json().get('hourly', {}).get('precipitation_probability', [])
        return max(probs) if probs else 0
    except:
        return 0

def dashboard(request):
    return render(request, 'visualization/dashboard.html')

def get_sensor_data(request):
    parcels = Parcel.objects.filter(is_active=True)
    total_parcels = parcels.count()
    
    avg_temp = 0
    avg_moist = 0
    parcel_data = []
    datasets = []
    labels = []
    
    for idx, p in enumerate(parcels):
        last_entry = SensorData.objects.filter(parcel=p).order_by('-timestamp').first()
        temp = last_entry.temperature if last_entry else 0
        moist = last_entry.soil_moisture if last_entry else 0
        
        avg_temp += temp
        avg_moist += moist
        
        parcel_data.append({
            'id': p.id,
            'name': p.name,
            'moisture': round(moist, 1),
            'temperature': round(temp, 1),
            'is_irrigating': p.is_irrigating,
            'threshold': p.moisture_threshold,
        })
        
        if idx < 5:  # Limit chart to top 5 parcels
            # FR-01: Son 24 saatin filtresi ve tarayıcı dostu limit
            last_24h = timezone.now() - timedelta(hours=24)
            data_points = list(SensorData.objects.filter(
                parcel=p, 
                timestamp__gte=last_24h
            ).order_by('-timestamp')[:50][::-1])
            
            # Use the longest available timeline for labels
            if len(data_points) > len(labels):
                labels = [d.timestamp.strftime('%H:%M:%S') for d in data_points]
            
            datasets.append({
                'label': f"{p.name} Nem",
                'data': [d.soil_moisture for d in data_points],
                'borderColor': f'hsl({idx * 137 % 360}, 70%, 50%)',
                'backgroundColor': f'hsla({idx * 137 % 360}, 70%, 50%, 0.1)',
                'borderWidth': 2,
                'tension': 0.4,
                'yAxisID': 'y1'
            })
            datasets.append({
                'label': f"{p.name} Sıcaklık",
                'data': [d.temperature for d in data_points],
                'borderColor': f'hsl({(idx * 137 + 50) % 360}, 70%, 50%)',
                'borderWidth': 2,
                'tension': 0.4,
                'borderDash': [3, 3],
                'hidden': True,
                'yAxisID': 'y'
            })

    if total_parcels > 0:
        avg_temp = round(avg_temp / total_parcels, 1)
        avg_moist = round(avg_moist / total_parcels, 1)
        
    logs = ActivityLog.objects.all().order_by('-timestamp')[:5]
    log_data = [{"time": log.timestamp.strftime('%H:%M:%S'), "type": log.event_type, "desc": str(_(log.description))} for log in logs]
    
    response_data = {
        "labels": labels,
        "datasets": datasets,
        "avg_temp": avg_temp,
        "avg_moist": avg_moist,
        "parcels": parcel_data,
        "logs": log_data,
    }
    
    if request.user.is_staff:
        users = User.objects.all().values('id', 'username', 'is_staff')
        response_data['users'] = list(users)
        response_data['devices'] = [
            {"id": p.id, "name": p.name, "battery": f"{p.battery_level}%", "signal": f"{p.rssi} dBm", "status": "Active" if p.is_active else "Inactive", "threshold": p.moisture_threshold} for p in parcels
        ]

    return JsonResponse(response_data)

@require_POST
def api_irrigate(request):
    try:
        data = json.loads(request.body)
        parcel_id = data.get('parcel_id')
        if parcel_id:
            parcel = Parcel.objects.get(id=parcel_id)
            if not parcel.is_irrigating:
                rain_prob = check_rain_probability()
                user = request.user if request.user.is_authenticated else None
                ip_addr = get_client_ip(request)

                if rain_prob > 60:
                    ActivityLog.objects.create(
                        event_type='WARNING', 
                        description=f'Yağış beklentisi nedeniyle sulama ertelendi ({parcel.name})',
                        user=user, ip_address=ip_addr
                    )
                    return JsonResponse({"status": "warning", "message": str(_("Yağış beklentisi nedeniyle sulama ertelendi."))})

                parcel.is_irrigating = True
                parcel.save()
                ActivityLog.objects.create(
                    event_type='SUCCESS', 
                    description=f'{parcel.name} için Manuel Sulama Başlatıldı',
                    user=user, ip_address=ip_addr
                )
                return JsonResponse({"status": "success", "message": str(_("Irrigation started."))})
            return JsonResponse({"status": "info", "message": str(_("Already irrigating."))})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)
    return JsonResponse({"status": "error", "message": "Invalid request"})

@require_POST
def api_update_threshold(request):
    if not request.user.is_staff:
        return JsonResponse({"status": "error", "message": "Unauthorized"}, status=403)
    try:
        data = json.loads(request.body)
        parcel_id = data.get('parcel_id')
        threshold = float(data.get('threshold', 25.0))
        if parcel_id:
            parcel = Parcel.objects.get(id=parcel_id)
            parcel.moisture_threshold = threshold
            parcel.save()
            ActivityLog.objects.create(
                event_type='INFO', 
                description=f'{parcel.name} için eşik değeri %{threshold} olarak güncellendi',
                user=request.user if request.user.is_authenticated else None,
                ip_address=get_client_ip(request)
            )
            return JsonResponse({"status": "success", "message": str(_("Threshold updated."))})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)
    return JsonResponse({"status": "error", "message": "Invalid request"})

@require_GET
def api_export_report(request):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.drawString(100, 750, "ATYS System Report")
    
    y = 700
    p.drawString(100, y, "Recent Sensor Data:")
    y -= 20
    for d in SensorData.objects.all().order_by('-timestamp')[:5]:
        p.drawString(120, y, f"{d.timestamp.strftime('%Y-%m-%d %H:%M:%S')} - Temp: {d.temperature}C, Moist: {d.soil_moisture}%")
        y -= 15

    y -= 20
    p.drawString(100, y, "Recent Logs:")
    y -= 20
    for log in ActivityLog.objects.all().order_by('-timestamp')[:5]:
        p.drawString(120, y, f"{log.timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {log.event_type}: {log.description}")
        y -= 15

    p.showPage()
    p.save()
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="atys_report.pdf"'
    return response

@require_POST
def api_update_profile(request):
    try:
        data = json.loads(request.body)
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({"status": "error", "message": "Unauthorized"}, status=401)
        
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'password' in data and data['password']:
            user.set_password(data['password'])
            
        user.save()
        return JsonResponse({"status": "success", "message": str(_("Profile updated."))})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)
