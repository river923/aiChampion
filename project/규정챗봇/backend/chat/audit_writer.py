from audit.models import QueryAuditLog
from characters.models import AICharacter
from chat.types import AnswerResult


def write_audit(user_id: int, character: AICharacter, question: str, result: AnswerResult) -> None:
    QueryAuditLog.objects.create(
        user_id=user_id,
        character=character,
        question=question,
        answer_preview=result.answer[:500],
        citation_summary="\n".join(c.title for c in result.citations),
        status=result.status,
        error_message=result.error_message,
    )
