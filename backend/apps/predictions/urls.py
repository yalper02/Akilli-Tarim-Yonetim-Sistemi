from django.urls import path

from .views import PredictionViewSet

urlpatterns = [
    path(
        "farms/<int:farm_id>/predictions/",
        PredictionViewSet.as_view({"get": "list"}),
        name="farm-prediction-list",
    ),
    path(
        "predictions/<int:pk>/",
        PredictionViewSet.as_view({"get": "retrieve"}),
        name="prediction-detail",
    ),
    path(
        "farms/<int:farm_id>/predictions/run/",
        PredictionViewSet.as_view({"post": "run"}),
        name="farm-prediction-run",
    ),
]
