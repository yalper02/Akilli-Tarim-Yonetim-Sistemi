from rest_framework.permissions import SAFE_METHODS, BasePermission

from .models import FarmMembership, Role


class IsFarmMember(BasePermission):
    """
    Grants access only to users who are members of the target farm.

    Resolves the farm via:
      1. `farm_id` URL kwarg (nested routes like /farms/{farm_id}/devices/)
      2. `obj.farm` attribute (object-level check for flat routes like /devices/{id}/)
      3. `obj` itself when obj IS the farm
    """

    message = "You are not a member of this farm."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        farm_id = view.kwargs.get("farm_id")
        if farm_id is None:
            return True  # defer to has_object_permission
        return FarmMembership.objects.filter(user=request.user, farm_id=farm_id).exists()

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        farm = getattr(obj, "farm", obj)
        return FarmMembership.objects.filter(user=request.user, farm=farm).exists()


class IsFarmManager(BasePermission):
    """
    Read access for all farm members; write access only for farm_manager / system_admin.
    Pair with IsFarmMember — this class only checks role, not membership.
    """

    message = "Farm manager or system admin role required."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        farm_id = view.kwargs.get("farm_id")
        if farm_id is None:
            return True  # defer to has_object_permission
        return FarmMembership.objects.filter(
            user=request.user,
            farm_id=farm_id,
            role__name__in=[Role.FARM_MANAGER, Role.SYSTEM_ADMIN],
        ).exists()

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        farm = getattr(obj, "farm", obj)
        return FarmMembership.objects.filter(
            user=request.user,
            farm=farm,
            role__name__in=[Role.FARM_MANAGER, Role.SYSTEM_ADMIN],
        ).exists()
