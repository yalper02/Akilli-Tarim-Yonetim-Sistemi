from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from apps.accounts.models import FarmMembership, Role
from apps.accounts.permissions import IsFarmManager, IsFarmMember

from .models import Crop, Farm
from .serializers import (
    CropSerializer,
    FarmSerializer,
    MembershipCreateSerializer,
    MembershipSerializer,
)


class CropViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Crop.objects.all()
    serializer_class = CropSerializer
    permission_classes = [IsAuthenticated]


class FarmViewSet(viewsets.ModelViewSet):
    serializer_class = FarmSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Farm.objects.filter(memberships__user=self.request.user)
            .select_related("crop", "owner")
            .distinct()
        )

    def perform_create(self, serializer):
        farm = serializer.save(owner=self.request.user)
        manager_role = Role.objects.get(name=Role.FARM_MANAGER)
        FarmMembership.objects.create(user=self.request.user, farm=farm, role=manager_role)


class FarmMembershipViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsAuthenticated, IsFarmMember, IsFarmManager]

    def get_queryset(self):
        return FarmMembership.objects.filter(farm_id=self.kwargs["farm_id"]).select_related(
            "user", "role"
        )

    def get_serializer_class(self):
        if self.action == "create":
            return MembershipCreateSerializer
        return MembershipSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["farm_id"] = self.kwargs["farm_id"]
        return ctx

    def perform_create(self, serializer):
        serializer.save(farm_id=self.kwargs["farm_id"])
