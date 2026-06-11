from pathlib import Path

from django.conf import settings

from characters.models import AICharacter
from chat.citations import citation_text
from indexing.models import ClauseIndex

DEFAULT_GUIDELINE_TEXT = (
    "1. 두괄식: 질문에 대한 핵심 결론이나 답변을 첫 문장에 가장 먼저 명확하게 제시하라.\n"
    "2. 간결성 및 가독성: 불필요한 수식어를 빼고 문장을 간결하게 작성하며, 읽기 편하도록 적절히 줄바꿈을 해라.\n"
    "3. 서술형 문장: '[확인 결과]', '[관련 기준]' 등 딱딱한 목차 템플릿을 쓰지 말고, 자연스러운 문장으로 서술하라.\n"
    "4. 근거 표기: 답변 내용의 맨 마지막 줄에는 반드시 '(근거) 규정명 제X조' 형식으로 출처를 남겨라. (예: (근거) 인사규정 제10조)"
)


def build_prompt(character: AICharacter, question: str, clauses: list[ClauseIndex]) -> str:
    evidence = "\n\n".join(f"[{citation_text(clause)}]\n{clause.body}" for clause in clauses)
    persona_text = _persona_instruction(character)
    evidence_instruction = _evidence_instruction(character, clauses, _guideline_text())
    return (
        "너는 사내 규정 근거형 AI 캐릭터다.\n"
        f"캐릭터명: {character.name}\n"
        f"담당 업무 요약: {character.description} ({character.duty_keywords})\n"
        f"{persona_text}\n"
        "---\n"
        "[대화 지침]\n"
        "1. 사용자가 '안녕', '누구야?' 등 가벼운 인사나 질문을 하면, 제공된 페르소나에 맞춰 친절하고 자연스럽게 인사하고, 자신이 어떤 업무를 안내할 수 있는지(담당 업무 요약 참고) 소개하라.\n"
        "2. 인사나 소개말의 경우 'missing_evidence_reason'이나 'citations'는 비워두어도 좋다.\n"
        f"{evidence_instruction}\n\n"
        f"질문: {question}\n\n"
        f"[근거]:\n{evidence if evidence else '없음'}"
    )


def _persona_instruction(character: AICharacter) -> str:
    if not character.persona_prompt:
        return ""
    return f"\n[당신의 페르소나 및 성격 지침]\n{character.persona_prompt}\n이 성격과 말투를 무조건 유지하십시오.\n"


def _evidence_instruction(character: AICharacter, clauses: list[ClauseIndex], guideline_text: str) -> str:
    if character.is_unrestricted:
        return (
            "너는 제한 없이 사용자와 대화할 수 있는 기관 통합 AI이다.\n"
            "답변(answer) 본문을 작성할 때 다음 [공무원 스타일 작성 지침]을 가급적 준수하며, 주어진 질문에 대해 자유롭고 풍부하게 답변하라.\n"
            f"--- 지침 시작 ---\n{guideline_text}\n--- 지침 끝 ---\n"
            "답변 구조 정보인 'citations'나 'missing_evidence_reason'은 필요 없다면 비워두어도 무방하다.\n"
        )
    if clauses:
        return (
            "아래 제공된 [근거] 안에서만 업무 관련 답변을 해야 한다.\n"
            "답변(answer) 본문을 작성할 때 다음 [공무원 스타일 작성 지침]을 반드시 준수하라:\n"
            f"--- 지침 시작 ---\n{guideline_text}\n--- 지침 끝 ---\n"
            "답변 구조 정보인 'citations' 목록에도 사용한 규정명과 조항을 정확히 포함해라.\n"
            "근거가 부족하다면 'missing_evidence_reason'을 작성하고, 'answer'에는 안내가 어렵다고 정중하고 간결하게 답하라.\n"
            "대답을 하지 못하는 경우('missing_evidence_reason' 작성 시)에만 'contact' 필드에 관련 담당자 연락처 정보를 채워라.\n"
        )
    return (
        "현재 등록된 근거 문서가 없습니다. 규정 관련 질문이라면 'missing_evidence_reason'을 작성하고, 'answer'에는 아직 규정 문서가 없어서 안내가 불가능하다고 공무원 스타일로 정중하고 간결하게 답하라.\n"
        "답변이 불가능한 경우이므로 'contact' 필드에 담당자 연락처 정보를 채워라.\n"
    )


def _guideline_text() -> str:
    guideline_path = Path(settings.BASE_DIR).parent / "docs" / "LLM_답변지침.md"
    try:
        return guideline_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return DEFAULT_GUIDELINE_TEXT
