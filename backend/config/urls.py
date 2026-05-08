from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


def health(request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health),
    # Kimlik doğrulama
    path("api/v1/auth/", include("apps.accounts.urls")),
    # Çiftlik ve ürün
    path("api/v1/", include("apps.farms.urls")),
    # Cihaz ve yetenek
    path("api/v1/", include("apps.devices.urls")),
    # Sensör verisi
    path("api/v1/", include("apps.sensor_data.urls")),
    # Kural motoru
    path("api/v1/", include("apps.rules.urls")),
    # Komutlar
    path("api/v1/", include("apps.commands.urls")),
    # Gübre
    path("api/v1/", include("apps.fertilization.urls")),
    # Bildirimler
    path("api/v1/", include("apps.notifications.urls")),
    # Tahminler
    path("api/v1/", include("apps.predictions.urls")),
    # Denetim günlükleri
    path("api/v1/", include("apps.audit.urls")),
    # Export (CSV / Excel)
    path("api/v1/", include("apps.exports.urls")),
    # API şema / Swagger UI
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]
