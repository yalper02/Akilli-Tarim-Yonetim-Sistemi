from rest_framework import serializers

from apps.accounts.models import FarmMembership

from .models import Crop, Farm


class CropSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crop
        fields = "__all__"


class FarmSerializer(serializers.ModelSerializer):
    crop_name = serializers.CharField(source="crop.name", read_only=True)
    owner_username = serializers.CharField(source="owner.username", read_only=True)

    class Meta:
        model = Farm
        fields = [
            "id",
            "name",
            "location",
            "latitude",
            "longitude",
            "area_hectares",
            "crop",
            "crop_name",
            "owner",
            "owner_username",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "owner", "owner_username", "created_at", "updated_at"]


class MembershipSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    role_display = serializers.CharField(source="role.get_name_display", read_only=True)

    class Meta:
        model = FarmMembership
        fields = ["id", "user", "username", "farm", "role", "role_display", "joined_at"]
        read_only_fields = ["id", "farm", "joined_at"]


class MembershipCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FarmMembership
        fields = ["id", "user", "role", "joined_at"]
        read_only_fields = ["id", "joined_at"]

    def validate(self, attrs):
        farm_id = self.context["farm_id"]
        user = attrs["user"]
        if FarmMembership.objects.filter(user=user, farm_id=farm_id).exists():
            raise serializers.ValidationError(
                {"detail": "Bu kullanıcı zaten çiftliğin üyesi.", "code": "already_member"}
            )
        return attrs
