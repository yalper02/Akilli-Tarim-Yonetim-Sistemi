from django.contrib import admin

from .models import DeviceTelemetry, SensorReading


@admin.register(SensorReading)
class SensorReadingAdmin(admin.ModelAdmin):
    list_display = ("device", "capability_type", "value", "time")
    list_filter = ("capability_type",)
    date_hierarchy = "time"


@admin.register(DeviceTelemetry)
class DeviceTelemetryAdmin(admin.ModelAdmin):
    list_display = ("device", "battery_level", "rssi", "time")
    date_hierarchy = "time"
