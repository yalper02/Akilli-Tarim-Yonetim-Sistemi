from django.db import models

class Parcel(models.Model):
    name = models.CharField(max_length=50, unique=True)
    location_coord = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    last_moisture = models.FloatField(default=0.0)
    moisture_threshold = models.FloatField(default=25.0)
    is_irrigating = models.BooleanField(default=False)
    battery_level = models.FloatField(default=100.0)
    rssi = models.IntegerField(default=-50)

    def __str__(self):
        return self.name

class SensorData(models.Model):
    parcel = models.ForeignKey(Parcel, on_delete=models.CASCADE, related_name='sensor_data', null=True, blank=True, db_index=True)
    device_name = models.CharField(max_length=50, default="ESP32-Prototip")
    temperature = models.FloatField(verbose_name="Sıcaklık (°C)")
    humidity = models.FloatField(verbose_name="Hava Nemi (%)")
    soil_moisture = models.FloatField(verbose_name="Toprak Nemi (%)")
    battery_level = models.FloatField(null=True, blank=True)
    rssi = models.IntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        p_name = self.parcel.name if self.parcel else self.device_name
        return f"{p_name} - {self.timestamp.strftime('%H:%M:%S')}"

from django.contrib.auth.models import User

class ActivityLog(models.Model):
    event_type = models.CharField(max_length=50)
    description = models.TextField()
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.timestamp.strftime('%H:%M:%S')} - {self.description}"

class SystemState(models.Model):
    is_irrigating = models.BooleanField(default=False)
    moisture_threshold = models.FloatField(default=25.0)
