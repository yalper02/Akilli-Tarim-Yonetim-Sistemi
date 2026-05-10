from django.contrib import admin
from django.urls import path
from django.http import HttpResponse

def home(request):
    return HttpResponse("Akıllı Tarım Sistemi çalışıyor 🚀")

urlpatterns = [
    path('', home),  # 👈 ana sayfa
    path('admin/', admin.site.urls),
]