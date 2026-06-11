from django.contrib import admin
from unfold.admin import ModelAdmin
from django.contrib import messages

from documents.models import RegulationDocument
from documents.services import parse_document


@admin.action(description="선택한 문서를 파싱하고 조항 인덱스를 갱신")
def parse_selected_documents(
    modeladmin: ModelAdmin,
    request: object,
    queryset: object,
) -> None:
    parsed_count = 0
    for document in queryset:
        parse_document(document)
        parsed_count += 1
    modeladmin.message_user(request, f"{parsed_count}개 문서를 파싱했습니다.", messages.SUCCESS)


@admin.register(RegulationDocument)
class RegulationDocumentAdmin(ModelAdmin):
    list_display = (
        "title",
        "character",
        "revision_date",
        "status",
        "is_latest",
        "updated_at",
    )
    list_filter = ("status", "is_latest", "character")
    search_fields = ("title", "parsed_markdown")
    actions = [parse_selected_documents]

    def save_model(self, request, obj, form, change):
        # 먼저 기본 저장 로직을 수행하여 파일이 물리적으로 저장되게 합니다.
        super().save_model(request, obj, form, change)

        # 파일이 방금 저장되어 '업로드(uploaded)' 상태인 경우 즉시 파싱 수행
        if obj.status == RegulationDocument.Status.UPLOADED:
            try:
                parse_document(obj)
                messages.success(request, f"[{obj.title}] 문서의 HWP/PDF 파싱 및 조항 인덱싱이 자동으로 완료되었습니다.")
            except Exception as e:
                messages.error(request, f"[{obj.title}] 문서 자동 파싱 중 오류가 발생했습니다: {e}")

# Register your models here.
