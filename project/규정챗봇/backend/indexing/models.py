from django.db import models


class ClauseIndex(models.Model):
    document = models.ForeignKey(
        "documents.RegulationDocument",
        on_delete=models.CASCADE,
        related_name="clauses",
        verbose_name="소속 규정 문서",
    )
    article = models.CharField(max_length=40, verbose_name="조 (Article)")
    paragraph = models.CharField(max_length=40, blank=True, verbose_name="항/호 (Paragraph)")
    title = models.CharField(max_length=200, blank=True, verbose_name="조항 제목")
    body = models.TextField(verbose_name="조항 본문")
    keywords = models.TextField(blank=True, verbose_name="추출된 키워드")
    is_active = models.BooleanField(default=True, verbose_name="활성화 여부")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")

    class Meta:
        verbose_name = "조항 인덱스"
        verbose_name_plural = "조항 인덱스 목록"
        ordering = ["document__title", "id"]

    def __str__(self) -> str:
        suffix = f" {self.paragraph}" if self.paragraph else ""
        return f"{self.document.title} {self.article}{suffix}"

# Create your models here.
