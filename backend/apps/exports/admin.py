from django.contrib import admin

from .models import ExportJob


@admin.register(ExportJob)
class ExportJobAdmin(admin.ModelAdmin):
    list_display = ["job_id", "requested_by", "format", "status", "row_count", "created_at"]
    list_filter = ["status", "format"]
    readonly_fields = ["job_id", "requested_by", "filters", "file_path", "row_count", "created_at"]
