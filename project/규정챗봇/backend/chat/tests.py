import json

import pytest
from django.contrib.auth.models import User
from django.test import Client

from characters.models import AICharacter
from documents.models import RegulationDocument
from indexing.models import ClauseIndex
from orgs.models import OrganizationUnit


@pytest.mark.django_db
def test_ask_question_when_evidence_exists_but_secret_missing() -> None:
    user = User.objects.create_user(username="demo", password="pass")
    character = _character()
    document = RegulationDocument.objects.create(
        character=character,
        title="성과평가지침",
        parsed_markdown="제1조",
        status=RegulationDocument.Status.PARSED,
    )
    ClauseIndex.objects.create(
        document=document,
        article="제1조",
        paragraph="제1항",
        body="성과평가 등급은 평가 기준에 따라 산정한다.",
    )
    client = Client()
    client.force_login(user)

    response = client.post(
        "/api/chat/ask/",
        data=json.dumps({"character_id": character.pk, "question": "성과평가 등급"}),
        content_type="application/json",
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "missing_credential"
    assert "LLM API 설정" in payload["answer"]


@pytest.mark.django_db
def test_ask_question_when_not_logged_in() -> None:
    response = Client().post(
        "/api/chat/ask/",
        data=json.dumps({"character_id": 1, "question": "성과평가 등급"}),
        content_type="application/json",
    )

    assert response.status_code == 302


def _character() -> AICharacter:
    institution = OrganizationUnit.add_root(name="기관", kind="institution")
    team = institution.add_child(name="ESG성과혁신팀", kind="team")
    return AICharacter.objects.create(name="이평가", organization=team)
