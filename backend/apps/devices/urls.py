from django.urls import path

from .views import DeviceCapabilityViewSet, DeviceViewSet

urlpatterns = [
    # Çiftliğe bağlı cihaz listesi ve kayıt
    path(
        "farms/<int:farm_id>/devices/",
        DeviceViewSet.as_view({"get": "list", "post": "create"}),
        name="farm-device-list",
    ),
    # Tek cihaz işlemleri (object-level IsFarmMember kontrolü devreye girer)
    path(
        "devices/<int:pk>/",
        DeviceViewSet.as_view({"get": "retrieve", "patch": "partial_update", "delete": "destroy"}),
        name="device-detail",
    ),
    path(
        "devices/<int:pk>/health/",
        DeviceViewSet.as_view({"get": "health"}),
        name="device-health",
    ),
    # Cihaz yetenekleri
    path(
        "devices/<int:device_pk>/capabilities/",
        DeviceCapabilityViewSet.as_view({"get": "list", "post": "create"}),
        name="device-capability-list",
    ),
    path(
        "devices/<int:device_pk>/capabilities/<int:pk>/",
        DeviceCapabilityViewSet.as_view({"delete": "destroy"}),
        name="device-capability-detail",
    ),
]
