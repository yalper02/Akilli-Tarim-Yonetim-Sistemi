from django.contrib import admin

from .models import Command


@admin.register(Command)
class CommandAdmin(admin.ModelAdmin):
    list_display = ("command_uid", "device", "action_type", "triggered_by", "status", "issued_at")
    list_filter = ("action_type", "status", "triggered_by")
    search_fields = ("command_uid",)
    readonly_fields = ("command_uid", "issued_at")
