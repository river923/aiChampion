from django.db.models import Q

from characters.models import AICharacter
from indexing.models import ClauseIndex

POSTPOSITIONS = ("에서", "와", "과", "은", "는", "이", "가", "을", "를", "의", "에", "로", "으로", "관련된", "대해")


def find_relevant_clauses(character: AICharacter, question: str) -> list[ClauseIndex]:
    words = _extract_search_words(question)
    queryset = ClauseIndex.objects.filter(
        document__character=character,
        document__is_latest=True,
        document__status="parsed",
        is_active=True,
    )
    if not words:
        return list(queryset[:3])
    filtered_queryset = queryset.filter(_keyword_query(words))
    scored: list[tuple[int, ClauseIndex]] = []
    for clause in filtered_queryset:
        haystack = f"{clause.document.title} {clause.title} {clause.body}"
        score = sum(1 for word in words if word in haystack)
        if score > 0:
            scored.append((score, clause))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [clause for _, clause in scored[:3]]


def _extract_search_words(question: str) -> list[str]:
    words: list[str] = []
    for raw_word in question.split():
        word = _strip_postposition(raw_word)
        if len(word) >= 2:
            words.append(word)
    return words


def _strip_postposition(word: str) -> str:
    for postposition in POSTPOSITIONS:
        if word.endswith(postposition) and len(word) > len(postposition):
            return word[: -len(postposition)]
    return word


def _keyword_query(words: list[str]) -> Q:
    q_objects = Q()
    for word in words:
        q_objects |= Q(title__icontains=word) | Q(body__icontains=word) | Q(document__title__icontains=word)
    return q_objects
