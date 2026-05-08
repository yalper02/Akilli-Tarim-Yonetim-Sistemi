from django.contrib import admin

from .models import Crop, Farm


@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    list_display = ("name", "scientific_name", "frost_sensitivity")
    search_fields = ("name", "scientific_name")


@admin.register(Farm)
class FarmAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "crop", "area_hectares", "created_at")
    list_filter = ("crop",)
    search_fields = ("name", "owner__username")
