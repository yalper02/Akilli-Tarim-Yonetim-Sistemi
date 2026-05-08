from django.db import models


class Prediction(models.Model):
    YIELD = "yield"
    IRRIGATION_TIMING = "irrigation_timing"
    PREDICTION_TYPE_CHOICES = [
        (YIELD, "Yield"),
        (IRRIGATION_TIMING, "Irrigation Timing"),
    ]

    farm = models.ForeignKey("farms.Farm", on_delete=models.CASCADE, related_name="predictions")
    prediction_type = models.CharField(max_length=30, choices=PREDICTION_TYPE_CHOICES)
    predicted_value = models.FloatField()
    confidence_score = models.FloatField(null=True, blank=True)
    features_used = models.JSONField(default=dict, blank=True)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "predictions"
