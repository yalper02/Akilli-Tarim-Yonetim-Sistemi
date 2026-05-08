from django.contrib import admin

from .models import Prediction


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = (
        "farm",
        "prediction_type",
        "predicted_value",
        "confidence_score",
        "valid_from",
        "valid_until",
    )
    list_filter = ("prediction_type", "farm")
