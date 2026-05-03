from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.translation import gettext as _
from .models import SensorData, ActivityLog, SystemState

def dashboard(request):
    return render(request, 'visualization/dashboard.html')

def get_sensor_data(request):
    data_points = list(SensorData.objects.all().order_by('-timestamp')[:20][::-1])
    last_entry = data_points[-1] if data_points else None
    
    logs = ActivityLog.objects.all().order_by('-timestamp')[:5]
    log_data = [{"time": log.timestamp.strftime('%H:%M:%S'), "type": log.event_type, "desc": str(_(log.description))} for log in logs]
    
    state, created = SystemState.objects.get_or_create(id=1)
    
    response_data = {
        "labels": [d.timestamp.strftime('%H:%M:%S') for d in data_points],
        "temperature": [d.temperature for d in data_points],
        "soil_moisture": [d.soil_moisture for d in data_points],
        "last_temp": round(last_entry.temperature, 2) if last_entry else 0,
        "last_moist": round(last_entry.soil_moisture, 1) if last_entry else 0,
        "logs": log_data,
        "is_irrigating": state.is_irrigating
    }
    return JsonResponse(response_data)

@require_POST
def api_irrigate(request):
    state, created = SystemState.objects.get_or_create(id=1)
    if not state.is_irrigating:
        state.is_irrigating = True
        state.save()
        ActivityLog.objects.create(event_type='SUCCESS', description='Manual Irrigation Started')
        return JsonResponse({"status": "success", "message": str(_("Irrigation started."))})
    return JsonResponse({"status": "info", "message": str(_("Already irrigating."))})
