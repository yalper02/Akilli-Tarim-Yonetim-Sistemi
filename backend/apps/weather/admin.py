from django.contrib import admin

from .models import WeatherCache


@admin.register(WeatherCache)
class WeatherCacheAdmin(admin.ModelAdmin):
    list_display = ("farm", "fetched_at", "valid_until")
    list_filter = ("farm",)
