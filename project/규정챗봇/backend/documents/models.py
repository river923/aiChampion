from pathlib import Path

from django.core.exceptions import ValidationError
from django.db import models

ALLOWED_EXTENSIONS = {".hwp", ".hwpx", ".pdf"}
MAX_DOCUMENTS_PER_CHARACTER = 10


def validate_supported_document(value: object) -> None:
    name = getattr(value, "name", "")
    extension = Path(str(name)).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise ValidationError(
            "사용할 수 없는 파일 형식입니다. 규정챗봇은 .hwp, .hwpx, .pdf 파일만 지원합니다."
        )


class RegulationDocument(models.Model):
    class Status(models.TextChoices):
        UPLOADED = "uploaded", "업로드"
        PARSED = "parsed", "파싱완료"
        FAILED = "failed", "파싱실패"
        INACTIVE = "inactive", "비활성"

    character = models.ForeignKey(
        "characters.AICharacter",
        on_delete=models.CASCADE,
        related_name="documents",
        verbose_name="연결된 AI 캐릭터",
    )
    title = models.CharField(max_length=200, verbose_name="문서 제목")
    revision_date = models.DateField(blank=True, null=True, verbose_name="개정 일자")
    source_file = models.FileField(
        upload_to="raw/%Y/%m/",
        validators=[validate_supported_document],
        verbose_name="원본 파일 (HWP/PDF)",
    )
    parsed_markdown = models.TextField(blank=True, verbose_name="파싱된 마크다운")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.UPLOADED,
        verbose_name="처리 상태",
    )
    is_latest = models.BooleanField(default=True, verbose_name="최신 본 여부")
    parse_error = models.TextField(blank=True, verbose_name="파싱 오류 메시지")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일시")

    class Meta:
        ordering = ["title", "-created_at"]

    def __str__(self) -> str:
        return self.title

    def clean(self) -> None:
        if self.pk is None and hasattr(self, "character") and getattr(self.character, "pk", None):
            count = RegulationDocument.objects.filter(
                character=self.character,
                status__in=[self.Status.UPLOADED, self.Status.PARSED],
            ).count()
            if count >= MAX_DOCUMENTS_PER_CHARACTER:
                raise ValidationError("AI 캐릭터당 문서는 최대 10개까지 연결할 수 있습니다.")

# Create your models here.
