import os
from getpass import getpass

from django.core.management.base import BaseCommand
from django.utils import timezone

from secretstore.crypto import encrypt_secret
from secretstore.models import SecretCredential


class Command(BaseCommand):
    help = "LLM API 키(Gemini)를 안전하게 암호화하여 DB에 등록합니다."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--api-key-env",
            type=str,
            default="GEMINI_API_KEY",
            help="API 키를 읽을 환경변수 이름",
        )
        parser.add_argument("--model", type=str, default="gemini-3.5-flash", help="사용할 모델명")

    def handle(self, *args: str, **options: str) -> None:
        api_key_env = options["api_key_env"]
        api_key = os.getenv(api_key_env) or getpass(f"{api_key_env}: ")
        model_name = options["model"]

        if not api_key:
            self.stderr.write(self.style.ERROR("API 키가 비어 있어 등록을 중단합니다."))
            return

        provider = SecretCredential.Provider.GEMINI
        display_name = "Gemini 기본 연동키"

        # 기존 키 비활성화 및 삭제 (간소화)
        SecretCredential.objects.filter(provider=provider, display_name=display_name).delete()

        SecretCredential.objects.create(
            provider=provider,
            display_name=display_name,
            encrypted_api_key=encrypt_secret(api_key),
            key_last4=api_key[-4:] if len(api_key) >= 4 else "",
            model_name=model_name,
            is_active=True,
            last_tested_at=timezone.now(),
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"{provider} API 키가 성공적으로 암호화되어 등록되었습니다. (모델: {model_name})"
            )
        )
