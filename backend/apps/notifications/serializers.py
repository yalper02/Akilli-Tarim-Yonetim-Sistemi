from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id",
            "farm",
            "title",
            "message",
            "notification_type",
            "severity",
            "is_read",
            "related_object_type",
            "related_object_id",
            "created_at",
        ]
        read_only_fields = ["id", "farm", "created_at"]
