from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models


class SecretCredential(models.Model):
    class Provider(models.TextChoices):
        GEMINI = "gemini", "Gemini"
        OPENAI = "openai", "OpenAI"
        CLAUDE = "claude", "Claude"
        OPENROUTER = "openrouter", "OpenRouter"
        LOCAL = "local", "Local LLM"

    provider = models.CharField(max_length=20, choices=Provider.choices, verbose_name="API 제공자")
    display_name = models.CharField(max_length=120, verbose_name="표시 이름")
    encrypted_api_key = models.TextField(verbose_name="암호화된 API 키")
    key_last4 = models.CharField(max_length=4, blank=True, verbose_name="키 마지막 4자리")
    model_name = models.CharField(max_length=120, blank=True, verbose_name="사용 모델명")
    is_active = models.BooleanField(default=True, verbose_name="활성화 여부")
    last_tested_at = models.DateTimeField(blank=True, null=True, verbose_name="마지막 테스트 일시")
    rotated_at = models.DateTimeField(blank=True, null=True, verbose_name="키 교체 일시")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="created_secret_credentials",
        verbose_name="등록자",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일시")

    class Meta:
        verbose_name = "보안 키 관리"
        verbose_name_plural = "보안 키 목록"
        ordering = ["provider", "display_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "display_name"],
                name="unique_secret_provider_display_name",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.get_provider_display()} - {self.display_name}"

    @property
    def masked_key(self) -> str:
        if self.key_last4:
            return f"****{self.key_last4}"
        return "미설정"

# Create your models here.
