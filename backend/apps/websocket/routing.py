from django.urls import path

from .consumers import FarmLiveConsumer, NotificationConsumer

websocket_urlpatterns = [
    path("ws/farms/<int:farm_id>/live/", FarmLiveConsumer.as_asgi()),
    path("ws/notifications/", NotificationConsumer.as_asgi()),
]
