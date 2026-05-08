from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CropViewSet, FarmMembershipViewSet, FarmViewSet

router = DefaultRouter()
router.register(r"farms", FarmViewSet, basename="farm")
router.register(r"crops", CropViewSet, basename="crop")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "farms/<int:farm_id>/memberships/",
        FarmMembershipViewSet.as_view({"get": "list", "post": "create"}),
        name="farm-membership-list",
    ),
    path(
        "farms/<int:farm_id>/memberships/<int:pk>/",
        FarmMembershipViewSet.as_view({"delete": "destroy"}),
        name="farm-membership-detail",
    ),
]
