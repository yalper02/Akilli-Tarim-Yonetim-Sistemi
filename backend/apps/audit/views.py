from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["action_type", "resource_type", "user"]
    ordering = ["-time"]

    def get_queryset(self):
        # Yöneticiler tüm logları görebilir; diğerleri kendi loglarını
        user = self.request.user
        qs = AuditLog.objects.select_related("user")
        if not user.is_staff:
            qs = qs.filter(user=user)

        params = self.request.query_params
        if params.get("start"):
            qs = qs.filter(time__gte=params["start"])
        if params.get("end"):
            qs = qs.filter(time__lte=params["end"])
        return qs
