from django.contrib import admin

from .models import Device, DeviceCapability


class DeviceCapabilityInline(admin.TabularInline):
    model = DeviceCapability
    extra = 1


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ("name", "device_uid", "farm", "device_type", "status", "last_seen_at")
    list_filter = ("device_type", "status", "farm")
    search_fields = ("name", "device_uid")
    inlines = [DeviceCapabilityInline]


@admin.register(DeviceCapability)
class DeviceCapabilityAdmin(admin.ModelAdmin):
    list_display = ("device", "capability_type", "unit", "min_value", "max_value")
    list_filter = ("capability_type",)
