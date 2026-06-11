from dataclasses import dataclass

from anthropic import Anthropic
from django.conf import settings
from google import genai
from google.genai import types
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List, Optional
import threading
import os

# 전역 캐시를 통해 모델 중복 로드 방지 (Lazy Loading)
_local_model = None
_model_lock = threading.Lock()


@dataclass(frozen=True, slots=True)
class LLMResponse:
    content: str


class CitationSchema(BaseModel):
    document_title: str
    article: str
    paragraph: Optional[str] = None
    appendix: Optional[str] = None


class ContactSchema(BaseModel):
    department: str
    name: str
    position: str
    extension: str
    reason: str


class AnswerSchema(BaseModel):
    answer: str
    citations: List[CitationSchema]
    follow_up_question: Optional[str] = None
    recommended_character: Optional[str] = None
    contact: Optional[ContactSchema] = None
    confidence: str
    missing_evidence_reason: Optional[str] = None


class LLMProviderError(Exception):
    pass


class MissingCredentialError(LLMProviderError):
    pass


def generate_response(provider: str, api_key: str, model_name: str, prompt: str) -> LLMResponse:
    if not api_key:
        raise MissingCredentialError("LLM API 키가 설정되지 않았습니다.")
    match provider:
        case "gemini":
            return _generate_gemini(api_key, model_name or "gemini-3.5-flash", prompt)
        case "openai":
            return _generate_openai(api_key, model_name or "gpt-5.5", prompt)
        case "claude":
            return _generate_claude(api_key, model_name or "claude-sonnet-4-5", prompt)
        case "openrouter":
            return _generate_openrouter(api_key, model_name, prompt)
        case "local":
            return _generate_local(model_name, prompt)
        case _:
            raise LLMProviderError(f"지원하지 않는 LLM 공급자입니다: {provider}")


def _generate_gemini(api_key: str, model_name: str, prompt: str) -> LLMResponse:
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=AnswerSchema,
            temperature=0.1,
        )
    )
    return LLMResponse(content=response.text or "")


def _generate_openai(api_key: str, model_name: str, prompt: str) -> LLMResponse:
    client = OpenAI(api_key=api_key)

    schema_json = AnswerSchema.model_json_schema()
    system_prompt = "You must respond in valid JSON format only."
    prompt_with_json = f"{prompt}\n\nCRITICAL: Respond ONLY in valid JSON matching this schema:\n{schema_json}"

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt_with_json}
        ],
        temperature=0.1,
        response_format={"type": "json_object"}
    )
    return LLMResponse(content=response.choices[0].message.content or "")

def _generate_openrouter(api_key: str, model_name: str, prompt: str) -> LLMResponse:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
    schema_json = AnswerSchema.model_json_schema()
    system_prompt = "You must respond in valid JSON format only."
    prompt_with_json = f"{prompt}\n\nCRITICAL: Respond ONLY in valid JSON matching this schema:\n{schema_json}"

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt_with_json}
        ],
        temperature=0.1,
    )
    return LLMResponse(content=response.choices[0].message.content or "")


def _generate_claude(api_key: str, model_name: str, prompt: str) -> LLMResponse:
    client = Anthropic(api_key=api_key)
    response = client.messages.create(
        model=model_name,
        max_tokens=1200,
        messages=[{"role": "user", "content": prompt}],
    )
    text_parts = [block.text for block in response.content if block.type == "text"]
    return LLMResponse(content="\n".join(text_parts))


def _generate_local(model_name: str, prompt: str) -> LLMResponse:
    global _local_model

    try:
        from llama_cpp import Llama
    except ImportError as exc:
        raise LLMProviderError("로컬 LLM을 실행하려면 llama-cpp-python 패키지가 필요합니다.") from exc

    with _model_lock:
        if _local_model is None:
            models_dir = os.getenv("REGBOT_MODELS_DIR", os.path.join(settings.BASE_DIR, "models"))

            if not model_name or not model_name.endswith('.gguf'):
                # 기본 모델명이 없으면 models/ 폴더 내 첫 번째 .gguf 파일을 찾아서 사용
                available_models = [f for f in os.listdir(models_dir) if f.endswith('.gguf')]
                if not available_models:
                    raise LLMProviderError(f"로컬 모델을 찾을 수 없습니다: {models_dir} 폴더에 .gguf 파일이 없습니다.")
                model_name = available_models[0]

            model_path = os.path.join(models_dir, model_name)
            if not os.path.exists(model_path):
                raise LLMProviderError(f"로컬 모델 파일을 찾을 수 없습니다: {model_path}")

            try:
                # n_gpu_layers=-1 옵션으로 Mac Metal GPU 100% 활용
                _local_model = Llama(
                    model_path=model_path,
                    n_gpu_layers=-1,
                    n_ctx=8192,
                    verbose=False
                )
            except Exception as exc:
                raise LLMProviderError(f"로컬 모델 로드에 실패했습니다: {exc}") from exc

    schema_json = AnswerSchema.model_json_schema()

    # 2B 등 작은 모델이 지침을 잊지 않도록 강한 리마인더 추가
    strong_reminder = (
        "★★CRITICAL INSTRUCTION FOR ANSWER GENERATION★★\n"
        "1. MUST use Public Official Style (BLUF: Bottom-Line-Up-Front).\n"
        "2. MUST use natural narrative Korean sentences (NO rigid templates like [확인 결과]).\n"
        "3. MUST append '(근거) 규정명 제X조' at the VERY END of your 'answer' string.\n"
    )

    prompt_with_json = (
        f"{prompt}\n\n"
        f"{strong_reminder}\n"
        f"CRITICAL: Respond ONLY in valid JSON matching this schema:\n{schema_json}"
    )

    messages = [
        {"role": "user", "content": prompt_with_json}
    ]

    try:
        response = _local_model.create_chat_completion(
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=1024,
        )
        generated_text = response["choices"][0]["message"]["content"]
        return LLMResponse(content=generated_text)
    except Exception as exc:
        raise LLMProviderError(f"로컬 추론 중 오류 발생: {exc}") from exc


def active_provider_name() -> str:
    return str(settings.LLM_PROVIDER)
