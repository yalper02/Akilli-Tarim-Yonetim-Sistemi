from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import SensorDataViewSet

router = DefaultRouter()
router.register(r"sensor-data", SensorDataViewSet, basename="sensor-data")

urlpatterns = [
    path("", include(router.urls)),
]
