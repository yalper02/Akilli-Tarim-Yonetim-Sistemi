from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.permissions import IsFarmManager, IsFarmMember

from .models import Device, DeviceCapability
from .serializers import DeviceCapabilitySerializer, DeviceHealthSerializer, DeviceSerializer


class DeviceViewSet(viewsets.ModelViewSet):
    serializer_class = DeviceSerializer
    permission_classes = [IsAuthenticated, IsFarmMember, IsFarmManager]

    def get_queryset(self):
        farm_id = self.kwargs.get("farm_id")
        if farm_id:
            return Device.objects.filter(farm_id=farm_id).prefetch_related("capabilities")
        # Düz rota (/devices/{pk}/) — kullanıcının üye olduğu çiftliklerdeki cihazlar
        return (
            Device.objects.filter(farm__memberships__user=self.request.user)
            .prefetch_related("capabilities")
            .distinct()
        )

    def perform_create(self, serializer):
        serializer.save(farm_id=self.kwargs["farm_id"])

    @action(detail=True, methods=["get"])
    def health(self, request, farm_id=None, pk=None):
        device = self.get_object()
        latest = device.telemetry.order_by("-time").first()
        data = {
            "device_id": device.id,
            "status": device.status,
            "last_seen_at": device.last_seen_at,
            "battery_level": latest.battery_level if latest else None,
            "rssi": latest.rssi if latest else None,
        }
        return Response(DeviceHealthSerializer(data).data)


class DeviceCapabilityViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = DeviceCapabilitySerializer
    permission_classes = [IsAuthenticated, IsFarmMember, IsFarmManager]

    def get_queryset(self):
        return DeviceCapability.objects.filter(device_id=self.kwargs["device_pk"])

    def perform_create(self, serializer):
        serializer.save(device_id=self.kwargs["device_pk"])
