from django.contrib import admin
from unfold.admin import ModelAdmin, StackedInline

from characters.models import AICharacter
from documents.models import RegulationDocument


class RegulationDocumentInline(StackedInline):
    model = RegulationDocument
    extra = 1
    fields = ("title", "source_file", "revision_date", "status", "is_latest")
    readonly_fields = ("status",)


@admin.register(AICharacter)
class AICharacterAdmin(ModelAdmin):
    list_display = ("name", "organization", "is_active", "updated_at")
    list_filter = ("organization", "is_active")
    search_fields = ("name", "description", "duty_keywords")
    inlines = [RegulationDocumentInline]

    fieldsets = (
        (
            "기본 정보",
            {
                "fields": (
                    "name",
                    "organization",
                    "is_active",
                ),
            },
        ),
        (
            "역할 및 설명",
            {
                "fields": (
                    "description",
                    "duty_keywords",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "프롬프트 및 안내",
            {
                "fields": (
                    "persona_prompt",
                    "contact_policy_note",
                ),
                "classes": ("collapse",),
            },
        ),
    )

# Register your models here.
