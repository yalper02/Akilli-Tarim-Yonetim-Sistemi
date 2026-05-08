from rest_framework import serializers

from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True, allow_null=True)

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "time",
            "user",
            "username",
            "ip_address",
            "action_type",
            "resource_type",
            "resource_id",
            "details",
        ]
        read_only_fields = fields
