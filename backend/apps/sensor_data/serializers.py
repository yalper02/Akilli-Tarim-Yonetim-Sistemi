from rest_framework import serializers

from .models import DeviceTelemetry, SensorReading


class SensorReadingSerializer(serializers.ModelSerializer):
    device_uid = serializers.CharField(source="device.device_uid", read_only=True)

    class Meta:
        model = SensorReading
        fields = ["id", "time", "device", "device_uid", "capability_type", "value"]


class DeviceTelemetrySerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceTelemetry
        fields = ["id", "time", "device", "battery_level", "rssi"]


class TimeseriesPointSerializer(serializers.Serializer):
    bucket = serializers.DateTimeField()
    device_id = serializers.IntegerField()
    capability_type = serializers.CharField()
    avg_value = serializers.FloatField()
    min_value = serializers.FloatField()
    max_value = serializers.FloatField()
