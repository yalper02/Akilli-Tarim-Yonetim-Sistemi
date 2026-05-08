import uuid

from django.conf import settings
from django.db import models


class ExportJob(models.Model):
    CSV = "csv"
    EXCEL = "excel"
    FORMAT_CHOICES = [(CSV, "CSV"), (EXCEL, "Excel")]

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETE = "complete"
    FAILED = "failed"
    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (PROCESSING, "Processing"),
        (COMPLETE, "Complete"),
        (FAILED, "Failed"),
    ]

    job_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="export_jobs",
    )
    format = models.CharField(max_length=5, choices=FORMAT_CHOICES)
    filters = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=PENDING)
    file_path = models.CharField(max_length=500, blank=True)
    row_count = models.IntegerField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"ExportJob({self.job_id}, {self.format}, {self.status})"

    class Meta:
        db_table = "export_jobs"
        ordering = ["-created_at"]
