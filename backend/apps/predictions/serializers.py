from rest_framework import serializers

from .models import Prediction


class PredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prediction
        fields = [
            "id",
            "farm",
            "prediction_type",
            "predicted_value",
            "confidence_score",
            "features_used",
            "valid_from",
            "valid_until",
            "created_at",
        ]
        read_only_fields = ["id", "farm", "created_at"]
