from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "severity", "notification_type", "is_read", "created_at")
    list_filter = ("severity", "is_read", "notification_type")
    search_fields = ("title", "user__username")
