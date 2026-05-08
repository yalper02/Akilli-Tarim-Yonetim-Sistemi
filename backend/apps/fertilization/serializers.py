from rest_framework import serializers

from .models import FertilizationHistory, FertilizationRecommendation


class FertilizationRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = FertilizationRecommendation
        fields = [
            "id",
            "farm",
            "nutrient_type",
            "urgency",
            "status",
            "reasoning",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "farm", "status", "created_at", "updated_at"]


class FertilizationHistorySerializer(serializers.ModelSerializer):
    applied_by_username = serializers.CharField(
        source="applied_by.username", read_only=True, allow_null=True
    )

    class Meta:
        model = FertilizationHistory
        fields = [
            "id",
            "farm",
            "recommendation",
            "applied_by",
            "applied_by_username",
            "nutrient_type",
            "product_name",
            "volume_applied",
            "applied_at",
            "notes",
        ]
        read_only_fields = ["id", "farm", "applied_by"]
