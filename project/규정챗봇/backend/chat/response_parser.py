import json

from chat.types import ParsedCitation, ParsedContact, ParsedLLMAnswer

type JsonValue = None | bool | int | float | str | list["JsonValue"] | dict[str, "JsonValue"]


def parse_llm_answer(content: str) -> ParsedLLMAnswer:
    raw_payload = json.loads(_strip_markdown_fence(content).strip())
    if not isinstance(raw_payload, dict):
        raise json.JSONDecodeError("LLM response must be a JSON object", content, 0)
    return ParsedLLMAnswer(
        answer=_string_value(raw_payload.get("answer"), "답변을 생성할 수 없습니다."),
        citations=_parse_citations(raw_payload.get("citations")),
        contact=_parse_contact(raw_payload.get("contact")),
        confidence=_string_value(raw_payload.get("confidence"), ""),
        missing_evidence_reason=_string_value(raw_payload.get("missing_evidence_reason"), ""),
    )


def _strip_markdown_fence(content: str) -> str:
    text = content.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text


def _parse_citations(value: JsonValue) -> list[ParsedCitation]:
    if not isinstance(value, list):
        return []
    citations: list[ParsedCitation] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        citations.append(
            ParsedCitation(
                document_title=_string_value(item.get("document_title"), ""),
                article=_string_value(item.get("article"), ""),
                paragraph=_string_value(item.get("paragraph"), ""),
                appendix=_string_value(item.get("appendix"), ""),
            )
        )
    return citations


def _parse_contact(value: JsonValue) -> ParsedContact | None:
    if not isinstance(value, dict):
        return None
    return ParsedContact(
        department=_string_value(value.get("department"), ""),
        name=_string_value(value.get("name"), ""),
        position=_string_value(value.get("position"), ""),
        extension=_string_value(value.get("extension"), ""),
        reason=_string_value(value.get("reason"), ""),
    )


def _string_value(value: JsonValue, default: str) -> str:
    if isinstance(value, str):
        return value
    return default
