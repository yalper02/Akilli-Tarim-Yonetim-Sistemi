from django.db import models


class SensorReading(models.Model):
    CAPABILITY_CHOICES = [
        ("soil_moisture", "Soil Moisture"),
        ("temperature", "Temperature"),
        ("humidity", "Humidity"),
        ("ph_level", "pH Level"),
        ("nitrogen_level", "Nitrogen Level"),
        ("phosphorus_level", "Phosphorus Level"),
        ("potassium_level", "Potassium Level"),
    ]

    # time comes from the device — NOT auto_now_add. Hypertable partition key.
    time = models.DateTimeField()
    device = models.ForeignKey("devices.Device", on_delete=models.CASCADE, related_name="readings")
    capability_type = models.CharField(max_length=30, choices=CAPABILITY_CHOICES)
    value = models.FloatField()

    class Meta:
        db_table = "sensor_readings"
        indexes = [
            models.Index(fields=["device", "-time"], name="idx_readings_device_time"),
            models.Index(fields=["capability_type", "-time"], name="idx_readings_capability_time"),
        ]


class DeviceTelemetry(models.Model):
    # time comes from the device — NOT auto_now_add. Hypertable partition key.
    time = models.DateTimeField()
    device = models.ForeignKey("devices.Device", on_delete=models.CASCADE, related_name="telemetry")
    battery_level = models.IntegerField(null=True, blank=True)
    rssi = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "device_telemetry"
        indexes = [
            models.Index(fields=["device", "-time"], name="idx_telemetry_device_time"),
        ]
