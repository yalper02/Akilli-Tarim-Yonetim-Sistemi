from rest_framework import serializers

from .models import Device, DeviceCapability


class DeviceCapabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceCapability
        fields = ["id", "capability_type", "unit", "min_value", "max_value"]
        read_only_fields = ["id"]


class DeviceSerializer(serializers.ModelSerializer):
    capabilities = DeviceCapabilitySerializer(many=True, read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Device
        fields = [
            "id",
            "farm",
            "name",
            "device_uid",
            "device_type",
            "status",
            "status_display",
            "location_description",
            "installed_at",
            "last_seen_at",
            "mqtt_username",
            "capabilities",
        ]
        read_only_fields = [
            "id",
            "farm",
            "status",
            "last_seen_at",
            "mqtt_username",
            "mqtt_password_hash",
        ]


class DeviceHealthSerializer(serializers.Serializer):
    device_id = serializers.IntegerField()
    status = serializers.CharField()
    last_seen_at = serializers.DateTimeField(allow_null=True)
    battery_level = serializers.IntegerField(allow_null=True)
    rssi = serializers.IntegerField(allow_null=True)
