from django.conf import settings
from django.db import models

NUTRIENT_CHOICES = [
    ("nitrogen", "Nitrogen"),
    ("phosphorus", "Phosphorus"),
    ("potassium", "Potassium"),
    ("ph", "pH"),
]


class FertilizationRecommendation(models.Model):
    SCHEDULED = "scheduled"
    URGENT = "urgent"
    URGENCY_CHOICES = [
        (SCHEDULED, "Scheduled"),
        (URGENT, "Urgent"),
    ]
    PENDING = "pending"
    APPLIED = "applied"
    DISMISSED = "dismissed"
    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (APPLIED, "Applied"),
        (DISMISSED, "Dismissed"),
    ]

    farm = models.ForeignKey(
        "farms.Farm", on_delete=models.CASCADE, related_name="fertilization_recommendations"
    )
    nutrient_type = models.CharField(max_length=15, choices=NUTRIENT_CHOICES)
    urgency = models.CharField(max_length=10, choices=URGENCY_CHOICES, default=SCHEDULED)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    reasoning = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "fertilization_recommendations"


class FertilizationHistory(models.Model):
    farm = models.ForeignKey(
        "farms.Farm", on_delete=models.CASCADE, related_name="fertilization_history"
    )
    recommendation = models.ForeignKey(
        FertilizationRecommendation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="history_entries",
    )
    applied_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="fertilization_applications",
    )
    nutrient_type = models.CharField(max_length=15, choices=NUTRIENT_CHOICES)
    product_name = models.CharField(max_length=200, blank=True)
    volume_applied = models.FloatField(null=True, blank=True)
    applied_at = models.DateTimeField()
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "fertilization_history"
