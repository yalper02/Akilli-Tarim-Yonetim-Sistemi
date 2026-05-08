from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import FarmMembership, Role, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "phone", "is_staff", "is_active")
    fieldsets = UserAdmin.fieldsets + (("Extra", {"fields": ("phone",)}),)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(FarmMembership)
class FarmMembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "farm", "role", "joined_at")
    list_filter = ("role",)
