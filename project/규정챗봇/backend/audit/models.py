from django.conf import settings
from django.db import models


class QueryAuditLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="질의자",
    )
    character = models.ForeignKey(
        "characters.AICharacter",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="대상 AI 캐릭터",
    )
    question = models.TextField(verbose_name="질의 내용")
    answer_preview = models.TextField(blank=True, verbose_name="답변 요약")
    citation_summary = models.TextField(blank=True, verbose_name="참조 문서 요약")
    status = models.CharField(max_length=40, verbose_name="처리 상태")
    error_message = models.TextField(blank=True, verbose_name="오류 메시지")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")

    class Meta:
        verbose_name = "질의 감사 로그"
        verbose_name_plural = "질의 감사 로그 목록"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.status} {self.created_at:%Y-%m-%d %H:%M:%S}"

# Create your models here.
