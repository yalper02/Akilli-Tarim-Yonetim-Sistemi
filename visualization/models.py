from django.db import models

class SensorData(models.Model):
    device_name = models.CharField(max_length=50, default="ESP32-Prototip")
    temperature = models.FloatField(verbose_name="Sıcaklık (°C)")
    humidity = models.FloatField(verbose_name="Hava Nemi (%)")
    soil_moisture = models.FloatField(verbose_name="Toprak Nemi (%)")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.device_name} - {self.timestamp.strftime('%H:%M:%S')}"

class ActivityLog(models.Model):
    event_type = models.CharField(max_length=50)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.timestamp.strftime('%H:%M:%S')} - {self.description}"

class SystemState(models.Model):
    is_irrigating = models.BooleanField(default=False)
