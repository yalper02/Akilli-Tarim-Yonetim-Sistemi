from django.conf import settings
from django.db import models


class Notification(models.Model):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    SEVERITY_CHOICES = [
        (INFO, "Info"),
        (WARNING, "Warning"),
        (CRITICAL, "Critical"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    farm = models.ForeignKey(
        "farms.Farm", on_delete=models.CASCADE, null=True, blank=True, related_name="notifications"
    )
    title = models.CharField(max_length=300)
    message = models.TextField()
    notification_type = models.CharField(max_length=50)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default=INFO)
    is_read = models.BooleanField(default=False)
    related_object_type = models.CharField(max_length=50, blank=True)
    related_object_id = models.BigIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "notifications"
        indexes = [
            models.Index(fields=["user", "-created_at"], name="idx_notifications_user_time"),
            models.Index(fields=["user", "is_read"], name="idx_notifications_user_read"),
        ]
