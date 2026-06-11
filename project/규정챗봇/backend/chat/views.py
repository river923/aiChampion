import json
from dataclasses import dataclass

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from chat.services import answer_question
from orgs.models import OrganizationUnit


@dataclass(frozen=True, slots=True)
class ChatRequest:
    character_id: int
    question: str


@require_GET
@ensure_csrf_cookie
def csrf_token(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"csrfToken": get_token(request)})


@require_POST
def login_api(request: HttpRequest) -> JsonResponse:
    payload = _parse_login_payload(request)
    if isinstance(payload, JsonResponse):
        return payload
    user = authenticate(request, username=payload["username"], password=payload["password"])
    if user is None:
        return JsonResponse({"error": "아이디 또는 비밀번호가 올바르지 않습니다."}, status=400)
    login(request, user)
    return JsonResponse(
        {
            "authenticated": True,
            "username": user.get_username(),
            "csrfToken": get_token(request),
        }
    )


@require_GET
def login_status(request: HttpRequest) -> JsonResponse:
    return JsonResponse(
        {
            "authenticated": request.user.is_authenticated,
            "username": request.user.get_username() if request.user.is_authenticated else "",
        }
    )


@require_GET
def get_org_tree(request: HttpRequest) -> JsonResponse:
    annotated_list = OrganizationUnit.get_annotated_list()
    result = []
    for node, info in annotated_list:
        if not node.is_active:
            continue

        characters = [
            {
                "id": char.id,
                "name": char.name,
                "description": char.description,
                "duty_keywords": char.duty_keywords,
            }
            for char in node.ai_characters.filter(is_active=True)
        ]

        result.append({
            "id": node.id,
            "name": node.name,
            "kind": node.kind,
            "level": info["level"],
            "characters": characters,
        })

    return JsonResponse({"tree": result})


@login_required
@require_POST
def ask_question(request: HttpRequest) -> JsonResponse:
    parsed = _parse_chat_request(request)
    if isinstance(parsed, JsonResponse):
        return parsed
    result = answer_question(
        user_id=request.user.pk,
        character_id=parsed.character_id,
        question=parsed.question,
    )
    citations_json = [{"title": c.title, "body": c.body} for c in result.citations]
    return JsonResponse(
        {
            "status": result.status,
            "answer": result.answer,
            "citations": citations_json,
            "error_message": result.error_message,
        }
    )


def _parse_chat_request(request: HttpRequest) -> ChatRequest | JsonResponse:
    try:
        raw_payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON 요청 형식이 올바르지 않습니다."}, status=400)
    character_id = raw_payload.get("character_id")
    question = raw_payload.get("question")
    if not isinstance(character_id, int):
        return JsonResponse({"error": "character_id는 숫자여야 합니다."}, status=400)
    if not isinstance(question, str) or not question.strip():
        return JsonResponse({"error": "question은 비어 있을 수 없습니다."}, status=400)
    return ChatRequest(character_id=character_id, question=question.strip())


def _parse_login_payload(request: HttpRequest) -> dict[str, str] | JsonResponse:
    try:
        raw_payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON 요청 형식이 올바르지 않습니다."}, status=400)
    username = raw_payload.get("username")
    password = raw_payload.get("password")
    if not isinstance(username, str) or not username.strip():
        return JsonResponse({"error": "username은 비어 있을 수 없습니다."}, status=400)
    if not isinstance(password, str) or not password:
        return JsonResponse({"error": "password는 비어 있을 수 없습니다."}, status=400)
    return {"username": username.strip(), "password": password}
