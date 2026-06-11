from django.contrib import admin
from unfold.admin import ModelAdmin

from indexing.models import ClauseIndex


@admin.register(ClauseIndex)
class ClauseIndexAdmin(ModelAdmin):
    list_display = ("document", "article", "paragraph", "title", "is_active")
    list_filter = ("document", "is_active")
    search_fields = ("document__title", "article", "paragraph", "title", "body", "keywords")

# Register your models here.
