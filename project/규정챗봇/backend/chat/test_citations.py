import pytest

from characters.models import AICharacter
from chat.citations import collect_valid_citations
from chat.types import ParsedCitation, ParsedLLMAnswer
from documents.models import RegulationDocument
from indexing.models import ClauseIndex
from orgs.models import OrganizationUnit


@pytest.mark.django_db
def test_collect_valid_citations_when_document_title_and_article_partially_match() -> None:
    character = _character()
    document = RegulationDocument.objects.create(
        character=character,
        title="성과평가지침(2026년 개정)",
        parsed_markdown="제12조",
        status=RegulationDocument.Status.PARSED,
    )
    clause = ClauseIndex.objects.create(
        document=document,
        article="제12조",
        paragraph="제1항",
        title="평가등급",
        body="평가등급은 점수에 따라 산정한다.",
    )
    parsed_answer = ParsedLLMAnswer(
        answer="성과평가지침 제12조를 기준으로 판단합니다.",
        citations=[ParsedCitation(document_title="성과평가지침", article="12조")],
        contact=None,
        confidence="high",
        missing_evidence_reason="",
    )

    citations = collect_valid_citations(parsed_answer, [clause])

    assert len(citations) == 1
    assert citations[0].title == "[성과평가지침(2026년 개정) 제12조(평가등급)]"
    assert citations[0].body == "평가등급은 점수에 따라 산정한다."


def _character() -> AICharacter:
    institution = OrganizationUnit.add_root(name="기관", kind="institution")
    team = institution.add_child(name="ESG성과혁신팀", kind="team")
    return AICharacter.objects.create(name="이평가", organization=team)
