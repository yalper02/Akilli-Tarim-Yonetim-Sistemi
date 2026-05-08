from django.db import models


class Device(models.Model):
    SENSOR = "sensor"
    ACTUATOR = "actuator"
    COMBINED = "combined"
    DEVICE_TYPE_CHOICES = [
        (SENSOR, "Sensor"),
        (ACTUATOR, "Actuator"),
        (COMBINED, "Combined"),
    ]
    ONLINE = "online"
    OFFLINE = "offline"
    STATUS_CHOICES = [
        (ONLINE, "Online"),
        (OFFLINE, "Offline"),
    ]

    farm = models.ForeignKey("farms.Farm", on_delete=models.CASCADE, related_name="devices")
    name = models.CharField(max_length=200)
    device_uid = models.CharField(max_length=100, unique=True)
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPE_CHOICES, default=SENSOR)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=OFFLINE)
    location_description = models.CharField(max_length=300, blank=True)
    installed_at = models.DateTimeField(null=True, blank=True)
    last_seen_at = models.DateTimeField(null=True, blank=True)
    mqtt_username = models.CharField(max_length=100, blank=True)
    mqtt_password_hash = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.name} ({self.device_uid})"

    class Meta:
        db_table = "devices"


class DeviceCapability(models.Model):
    SOIL_MOISTURE = "soil_moisture"
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    PH_LEVEL = "ph_level"
    NITROGEN_LEVEL = "nitrogen_level"
    PHOSPHORUS_LEVEL = "phosphorus_level"
    POTASSIUM_LEVEL = "potassium_level"
    VALVE_CONTROL = "valve_control"
    FERTILIZER_DISPENSER = "fertilizer_dispenser"
    CAPABILITY_CHOICES = [
        (SOIL_MOISTURE, "Soil Moisture"),
        (TEMPERATURE, "Temperature"),
        (HUMIDITY, "Humidity"),
        (PH_LEVEL, "pH Level"),
        (NITROGEN_LEVEL, "Nitrogen Level"),
        (PHOSPHORUS_LEVEL, "Phosphorus Level"),
        (POTASSIUM_LEVEL, "Potassium Level"),
        (VALVE_CONTROL, "Valve Control"),
        (FERTILIZER_DISPENSER, "Fertilizer Dispenser"),
    ]

    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="capabilities")
    capability_type = models.CharField(max_length=30, choices=CAPABILITY_CHOICES)
    unit = models.CharField(max_length=20, blank=True)
    min_value = models.FloatField(null=True, blank=True)
    max_value = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = "device_capabilities"
        unique_together = [("device", "capability_type")]
