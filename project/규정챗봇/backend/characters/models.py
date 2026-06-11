from django.core.exceptions import ValidationError
from django.db import models


class AICharacter(models.Model):
    name = models.CharField(max_length=80, unique=True, verbose_name="캐릭터명")
    organization = models.ForeignKey(
        "orgs.OrganizationUnit",
        on_delete=models.PROTECT,
        related_name="ai_characters",
        verbose_name="소속 부서(조직)",
    )
    description = models.TextField(blank=True, verbose_name="캐릭터 설명")
    duty_keywords = models.TextField(blank=True, verbose_name="업무 키워드")
    persona_prompt = models.TextField(blank=True, verbose_name="페르소나 프롬프트")
    contact_policy_note = models.TextField(blank=True, verbose_name="담당자 안내 문구")
    is_unrestricted = models.BooleanField(default=False, verbose_name="자유 대화 모드(규정 제한 없음)")
    is_active = models.BooleanField(default=True, verbose_name="사용 여부")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일시")

    class Meta:
        verbose_name = "AI 캐릭터"
        verbose_name_plural = "AI 캐릭터 목록"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        if self.organization.kind not in ("team", "headquarters"):
            raise ValidationError("AI 캐릭터는 팀 또는 본부 단위 조직에 배치해야 합니다.")

# Create your models here.
