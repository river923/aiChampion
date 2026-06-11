import json

from characters.models import AICharacter
from chat.audit_writer import write_audit
from chat.citations import collect_valid_citations
from chat.prompts import build_prompt
from chat.response_parser import parse_llm_answer
from chat.retrieval import find_relevant_clauses
from chat.types import AnswerResult, ParsedLLMAnswer
from llm.providers import LLMProviderError, generate_response
from secretstore.crypto import decrypt_secret
from secretstore.models import SecretCredential


def answer_question(user_id: int, character_id: int, question: str) -> AnswerResult:
    character = AICharacter.objects.get(pk=character_id, is_active=True)
    clauses = [] if character.is_unrestricted else find_relevant_clauses(character, question)
    credential = _active_credential()
    if credential is None:
        result = AnswerResult(
            status="missing_credential",
            answer="LLM API 설정이 완료되지 않았습니다.",
            citations=[],
            error_message="관리자 페이지에서 사용할 LLM 공급자와 API 키를 등록해야 합니다.",
        )
        write_audit(user_id, character, question, result)
        return result
    try:
        response = generate_response(
            provider=credential.provider,
            api_key=decrypt_secret(credential.encrypted_api_key),
            model_name=credential.model_name,
            prompt=build_prompt(character, question, clauses),
        )
        parsed_answer = parse_llm_answer(response.content)
    except (LLMProviderError, json.JSONDecodeError) as exc:
        result = AnswerResult(
            status="llm_error",
            answer="LLM 응답 생성 또는 JSON 파싱 중 오류가 발생했습니다.",
            citations=[],
            error_message=str(exc),
        )
        write_audit(user_id, character, question, result)
        return result
    citations = collect_valid_citations(parsed_answer, clauses)
    if parsed_answer.missing_evidence_reason or (clauses and not citations):
        result = AnswerResult(
            status="no_evidence",
            answer=_answer_with_contact(parsed_answer),
            citations=citations,
        )
    else:
        result = AnswerResult(status="answered", answer=parsed_answer.answer, citations=citations)
    write_audit(user_id, character, question, result)
    return result


def _active_credential() -> SecretCredential | None:
    return SecretCredential.objects.filter(is_active=True).order_by("provider").first()


def _answer_with_contact(parsed_answer: ParsedLLMAnswer) -> str:
    answer = parsed_answer.answer or "질문하신 내용에 대한 정확한 근거를 확인할 수 없습니다."
    if parsed_answer.contact is None:
        return answer
    contact = parsed_answer.contact
    return (
        f"{answer}\n\n"
        "[담당자 안내]\n"
        f"{contact.reason}\n"
        f"- 부서: {contact.department}\n"
        f"- 담당자: {contact.name} {contact.position}\n"
        f"- 내선: {contact.extension}"
    )
