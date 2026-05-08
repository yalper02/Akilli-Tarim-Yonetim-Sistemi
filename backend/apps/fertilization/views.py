from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.permissions import IsFarmMember

from .models import FertilizationHistory, FertilizationRecommendation
from .serializers import FertilizationHistorySerializer, FertilizationRecommendationSerializer


class FertilizationRecommendationViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = FertilizationRecommendationSerializer
    permission_classes = [IsAuthenticated, IsFarmMember]

    def get_queryset(self):
        farm_id = self.kwargs.get("farm_id")
        if farm_id:
            return FertilizationRecommendation.objects.filter(
                farm_id=farm_id, status=FertilizationRecommendation.PENDING
            ).order_by("-created_at")
        return (
            FertilizationRecommendation.objects.filter(farm__memberships__user=self.request.user)
            .order_by("-created_at")
            .distinct()
        )

    @action(detail=True, methods=["post"])
    def apply(self, request, farm_id=None, pk=None):
        """Öneriyi uygulandı olarak işaretle ve geçmişe ekle."""
        rec = self.get_object()
        if rec.status != FertilizationRecommendation.PENDING:
            return Response(
                {"detail": "Bu öneri zaten işleme alınmış.", "code": "already_processed"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        from django.utils.timezone import now

        rec.status = FertilizationRecommendation.APPLIED
        rec.save(update_fields=["status", "updated_at"])

        FertilizationHistory.objects.create(
            farm=rec.farm,
            recommendation=rec,
            applied_by=request.user,
            nutrient_type=rec.nutrient_type,
            applied_at=now(),
        )
        return Response(FertilizationRecommendationSerializer(rec).data)

    @action(detail=True, methods=["post"])
    def dismiss(self, request, farm_id=None, pk=None):
        rec = self.get_object()
        if rec.status != FertilizationRecommendation.PENDING:
            return Response(
                {"detail": "Bu öneri zaten işleme alınmış.", "code": "already_processed"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        rec.status = FertilizationRecommendation.DISMISSED
        rec.save(update_fields=["status", "updated_at"])
        return Response(FertilizationRecommendationSerializer(rec).data)


class FertilizationHistoryViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = FertilizationHistorySerializer
    permission_classes = [IsAuthenticated, IsFarmMember]

    def get_queryset(self):
        farm_id = self.kwargs.get("farm_id")
        if farm_id:
            return (
                FertilizationHistory.objects.filter(farm_id=farm_id)
                .select_related("applied_by", "recommendation")
                .order_by("-applied_at")
            )
        return (
            FertilizationHistory.objects.filter(farm__memberships__user=self.request.user)
            .select_related("applied_by", "recommendation")
            .order_by("-applied_at")
            .distinct()
        )

    def perform_create(self, serializer):
        serializer.save(farm_id=self.kwargs["farm_id"], applied_by=self.request.user)
