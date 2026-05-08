from rest_framework import serializers

from .models import FarmMembership, Role, User


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "name"]


class FarmMembershipSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    farm_name = serializers.CharField(source="farm.name", read_only=True)

    class Meta:
        model = FarmMembership
        fields = ["id", "farm_id", "farm_name", "role", "joined_at"]


class UserSerializer(serializers.ModelSerializer):
    memberships = FarmMembershipSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone",
            "is_staff",
            "memberships",
        ]
        read_only_fields = ["id", "username", "is_staff"]


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "phone"]
