from django.contrib import admin
from unfold.admin import ModelAdmin

from audit.models import QueryAuditLog


@admin.register(QueryAuditLog)
class QueryAuditLogAdmin(ModelAdmin):
    list_display = ("created_at", "user", "character", "status")
    list_filter = ("status", "character")
    search_fields = ("question", "answer_preview", "citation_summary")
    readonly_fields = (
        "user",
        "character",
        "question",
        "answer_preview",
        "citation_summary",
        "status",
        "error_message",
        "created_at",
    )

# Register your models here.
