from rest_framework import mixins, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsFarmMember
from apps.commands.services import publish_command
from apps.devices.models import Device

from .models import Command
from .serializers import CommandSerializer, ManualCommandSerializer


class CommandViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = CommandSerializer
    permission_classes = [IsAuthenticated, IsFarmMember]

    def get_queryset(self):
        farm_id = self.kwargs.get("farm_id")
        if farm_id:
            return (
                Command.objects.filter(device__farm_id=farm_id)
                .select_related("device", "rule", "user")
                .order_by("-issued_at")
            )
        return (
            Command.objects.filter(device__farm__memberships__user=self.request.user)
            .select_related("device", "rule", "user")
            .order_by("-issued_at")
            .distinct()
        )


class ManualCommandView(APIView):
    """POST /devices/{device_id}/commands/ — el ile komut gönder (US-02)."""

    permission_classes = [IsAuthenticated, IsFarmMember]

    def post(self, request, device_id):
        try:
            device = Device.objects.select_related("farm").get(pk=device_id)
        except Device.DoesNotExist:
            return Response(
                {"detail": "Cihaz bulunamadı.", "code": "not_found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        # IsFarmMember nesne düzeyi kontrolü
        self.check_object_permissions(request, device)

        serializer = ManualCommandSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        command = publish_command(
            device=device,
            action_type=serializer.validated_data["action_type"],
            parameters=serializer.validated_data.get("parameters", {}),
            user=request.user,
        )
        return Response(CommandSerializer(command).data, status=status.HTTP_201_CREATED)
