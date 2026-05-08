from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from apps.accounts.permissions import IsFarmMember

from .models import Prediction
from .serializers import PredictionSerializer


class PredictionViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = PredictionSerializer
    permission_classes = [IsAuthenticated, IsFarmMember]

    def get_queryset(self):
        farm_id = self.kwargs.get("farm_id")
        from django.utils.timezone import now

        if farm_id:
            return Prediction.objects.filter(farm_id=farm_id, valid_until__gte=now()).order_by(
                "-created_at"
            )
        return (
            Prediction.objects.filter(
                farm__memberships__user=self.request.user, valid_until__gte=now()
            )
            .order_by("-created_at")
            .distinct()
        )

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated, IsAdminUser])
    def run(self, request, farm_id=None):
        """ML modelini el ile tetikle (yönetici)."""
        # Sprint 6'da implement edilecek — şimdi stub döner
        return Response(
            {
                "detail": "ML modeli kuyruğa alındı.",
                "farm_id": farm_id,
                "code": "prediction_queued",
            },
            status=status.HTTP_202_ACCEPTED,
        )
