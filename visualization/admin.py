from django.contrib import admin
from .models import Parcel, SensorData, SystemState, ActivityLog

@admin.register(Parcel)
class ParcelAdmin(admin.ModelAdmin):
    list_display = ('name', 'location_coord', 'battery_level', 'get_last_updated', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'location_coord')

    def get_last_updated(self, obj):
        latest = obj.sensor_data.order_by('-timestamp').first()
        if latest:
            return latest.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        return "Veri Yok"
    get_last_updated.short_description = 'Son Güncellenme'

@admin.register(SensorData)
class SensorDataAdmin(admin.ModelAdmin):
    list_display = ('get_parcel_name', 'temperature', 'soil_moisture', 'timestamp')
    list_filter = ('parcel__name', 'timestamp')
    search_fields = ('parcel__name', 'device_name')

    def get_parcel_name(self, obj):
        return obj.parcel.name if obj.parcel else obj.device_name
    get_parcel_name.short_description = 'Parsel / Cihaz'

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'description', 'user', 'ip_address', 'timestamp')
    list_filter = ('event_type', 'timestamp', 'user')
    search_fields = ('description', 'ip_address')

@admin.register(SystemState)
class SystemStateAdmin(admin.ModelAdmin):
    list_display = ('is_irrigating', 'moisture_threshold')
