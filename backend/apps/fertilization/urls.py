from django.urls import path

from .views import FertilizationHistoryViewSet, FertilizationRecommendationViewSet

urlpatterns = [
    # Gübre önerileri
    path(
        "farms/<int:farm_id>/fertilization/recommendations/",
        FertilizationRecommendationViewSet.as_view({"get": "list"}),
        name="farm-fertilization-recommendation-list",
    ),
    path(
        "fertilization/recommendations/<int:pk>/",
        FertilizationRecommendationViewSet.as_view({"get": "retrieve"}),
        name="fertilization-recommendation-detail",
    ),
    path(
        "fertilization/recommendations/<int:pk>/apply/",
        FertilizationRecommendationViewSet.as_view({"post": "apply"}),
        name="fertilization-recommendation-apply",
    ),
    path(
        "fertilization/recommendations/<int:pk>/dismiss/",
        FertilizationRecommendationViewSet.as_view({"post": "dismiss"}),
        name="fertilization-recommendation-dismiss",
    ),
    # Gübre geçmişi
    path(
        "farms/<int:farm_id>/fertilization/history/",
        FertilizationHistoryViewSet.as_view({"get": "list", "post": "create"}),
        name="farm-fertilization-history",
    ),
]
