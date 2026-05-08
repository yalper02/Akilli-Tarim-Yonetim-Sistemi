from rest_framework import serializers

from .models import ExportJob


class ExportRequestSerializer(serializers.Serializer):
    """CSV veya Excel export isteği için filtre parametreleri."""

    device_id = serializers.IntegerField(required=False)
    capability = serializers.CharField(required=False)
    start = serializers.DateTimeField(required=False)
    end = serializers.DateTimeField(required=False)


class ExportJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExportJob
        fields = [
            "job_id",
            "format",
            "filters",
            "status",
            "row_count",
            "error_message",
            "created_at",
            "expires_at",
        ]
        read_only_fields = fields
