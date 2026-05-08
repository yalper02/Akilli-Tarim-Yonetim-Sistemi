from django.urls import path

from .views import CommandViewSet, ManualCommandView

urlpatterns = [
    # Çiftliğe bağlı komut geçmişi
    path(
        "farms/<int:farm_id>/commands/",
        CommandViewSet.as_view({"get": "list"}),
        name="farm-command-list",
    ),
    # Tek komut detayı
    path(
        "commands/<int:pk>/",
        CommandViewSet.as_view({"get": "retrieve"}),
        name="command-detail",
    ),
    # El ile komut gönder (US-02)
    path(
        "devices/<int:device_id>/commands/",
        ManualCommandView.as_view(),
        name="device-manual-command",
    ),
]
