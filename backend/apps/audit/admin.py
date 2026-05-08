from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("time", "user", "action_type", "resource_type", "resource_id", "ip_address")
    list_filter = ("action_type", "resource_type")
    search_fields = ("user__username", "action_type")
    date_hierarchy = "time"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
