from rest_framework import serializers

from .models import Command


class CommandSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source="device.name", read_only=True)
    rule_name = serializers.CharField(source="rule.name", read_only=True, allow_null=True)
    user_username = serializers.CharField(source="user.username", read_only=True, allow_null=True)

    class Meta:
        model = Command
        fields = [
            "id",
            "command_uid",
            "device",
            "device_name",
            "rule",
            "rule_name",
            "user",
            "user_username",
            "action_type",
            "parameters",
            "status",
            "triggered_by",
            "issued_at",
            "executed_at",
        ]
        read_only_fields = [
            "id",
            "command_uid",
            "rule",
            "user",
            "status",
            "triggered_by",
            "issued_at",
            "executed_at",
        ]


class ManualCommandSerializer(serializers.Serializer):
    action_type = serializers.ChoiceField(choices=Command.ACTION_TYPE_CHOICES)
    parameters = serializers.JSONField(required=False, default=dict)
