from django.contrib import admin

from .models import FertilizationHistory, FertilizationRecommendation


@admin.register(FertilizationRecommendation)
class FertilizationRecommendationAdmin(admin.ModelAdmin):
    list_display = ("farm", "nutrient_type", "urgency", "status", "created_at")
    list_filter = ("urgency", "status", "nutrient_type")


@admin.register(FertilizationHistory)
class FertilizationHistoryAdmin(admin.ModelAdmin):
    list_display = ("farm", "nutrient_type", "applied_by", "product_name", "applied_at")
    list_filter = ("nutrient_type",)
