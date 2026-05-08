from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    # time is the action timestamp — NOT auto_now_add. Hypertable partition key.
    time = models.DateTimeField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    action_type = models.CharField(max_length=100)
    resource_type = models.CharField(max_length=100, blank=True)
    resource_id = models.BigIntegerField(null=True, blank=True)
    details = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "audit_logs"
        indexes = [
            models.Index(fields=["-time"], name="idx_audit_time"),
            models.Index(fields=["user", "-time"], name="idx_audit_user_time"),
        ]
