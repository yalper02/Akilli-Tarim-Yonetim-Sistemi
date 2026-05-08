from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.permissions import IsFarmManager, IsFarmMember

from .models import Rule
from .serializers import RuleSerializer


class RuleViewSet(viewsets.ModelViewSet):
    serializer_class = RuleSerializer
    permission_classes = [IsAuthenticated, IsFarmMember, IsFarmManager]

    def get_queryset(self):
        farm_id = self.kwargs.get("farm_id")
        if farm_id:
            return (
                Rule.objects.filter(farm_id=farm_id)
                .prefetch_related("conditions", "actions", "weather_constraint")
                .select_related("created_by")
            )
        return (
            Rule.objects.filter(farm__memberships__user=self.request.user)
            .prefetch_related("conditions", "actions", "weather_constraint")
            .select_related("created_by")
            .distinct()
        )

    def perform_create(self, serializer):
        serializer.save(
            farm_id=self.kwargs["farm_id"],
            created_by=self.request.user,
        )

    @action(detail=True, methods=["post"])
    def toggle(self, request, farm_id=None, pk=None):
        rule = self.get_object()
        rule.is_active = not rule.is_active
        rule.save(update_fields=["is_active", "updated_at"])
        return Response({"id": rule.id, "is_active": rule.is_active})

    @action(detail=True, methods=["post"])
    def test(self, request, farm_id=None, pk=None):
        """Kuru çalıştırma — tetiklenme durumunu raporlar, gerçek eylem yapmaz."""
        rule = self.get_object()
        if not rule.is_active:
            return Response({"would_trigger": False, "reason": "Kural aktif değil."})
        return Response(
            {
                "would_trigger": True,
                "rule_id": rule.id,
                "conditions_count": rule.conditions.count(),
                "actions_count": rule.actions.count(),
                "has_weather_constraint": hasattr(rule, "weather_constraint"),
                "note": "Kuru çalıştırma tamamlandı — gerçek sensör verisi kontrol edilmedi.",
            }
        )
