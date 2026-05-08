from django.conf import settings
from django.db import models


class Crop(models.Model):
    FROST_LOW = "low"
    FROST_MEDIUM = "medium"
    FROST_HIGH = "high"
    FROST_CHOICES = [
        (FROST_LOW, "Low"),
        (FROST_MEDIUM, "Medium"),
        (FROST_HIGH, "High"),
    ]

    name = models.CharField(max_length=100)
    scientific_name = models.CharField(max_length=150, blank=True)
    optimal_soil_moisture_min = models.FloatField()
    optimal_soil_moisture_max = models.FloatField()
    optimal_temperature_min = models.FloatField()
    optimal_temperature_max = models.FloatField()
    irrigation_water_need_mm_per_day = models.FloatField()
    optimal_ph_min = models.FloatField()
    optimal_ph_max = models.FloatField()
    nitrogen_need_ppm = models.FloatField()
    phosphorus_need_ppm = models.FloatField()
    potassium_need_ppm = models.FloatField()
    frost_sensitivity = models.CharField(max_length=10, choices=FROST_CHOICES, default=FROST_MEDIUM)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "crops"


class Farm(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=300, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    area_hectares = models.FloatField(null=True, blank=True)
    crop = models.ForeignKey(
        Crop, on_delete=models.SET_NULL, null=True, blank=True, related_name="farms"
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owned_farms"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "farms"
