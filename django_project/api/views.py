from django.http import JsonResponse

def sensor_data(request):
    return JsonResponse({
        "sicaklik": 28,
        "nem": 45
    })