from django.utils import timezone

from llm.providers import LLMProviderError, generate_response
from secretstore.crypto import decrypt_secret
from secretstore.models import SecretCredential


def test_credential_connection(credential: SecretCredential) -> str:
    prompt = "연결 테스트입니다. 'ok'만 답하세요."
    try:
        response = generate_response(
            provider=credential.provider,
            api_key=decrypt_secret(credential.encrypted_api_key),
            model_name=credential.model_name,
            prompt=prompt,
        )
    except LLMProviderError as exc:
        raise SecretConnectionError("LLM 연결 테스트에 실패했습니다.") from exc
    credential.last_tested_at = timezone.now()
    credential.save(update_fields=["last_tested_at", "updated_at"])
    return response.content[:100]


class SecretConnectionError(Exception):
    pass
