from django.core.management.base import BaseCommand

from characters.models import AICharacter
from orgs.models import OrganizationUnit, StaffProfile


class Command(BaseCommand):
    help = "가명 조직도와 데모 AI 캐릭터를 생성합니다."

    def handle(self, *args: str, **options: str) -> None:
        institution = _unit("한국산림복지진흥원", "institution", None)
        headquarters = _unit("본원", "headquarters", institution)
        division = _unit("미래전략본부", "office", headquarters)
        team = _unit("ESG성과혁신팀", "team", division)
        _staff(team)
        AICharacter.objects.get_or_create(
            name="이평가",
            defaults={
                "organization": team,
                "description": "성과평가 지침과 직무역량평가 운영지침을 안내하는 AI 캐릭터",
                "duty_keywords": "성과평가 평가등급 직무역량 이의신청 평가위원",
                "persona_prompt": "정확한 근거와 조항을 기준으로 답변한다.",
                "contact_policy_note": "운영 판단이 필요한 경우에만 담당자를 안내한다.",
            },
        )
        self.stdout.write(self.style.SUCCESS("데모 조직도와 AI 캐릭터를 생성했습니다."))


def _unit(
    name: str,
    kind: str,
    parent: OrganizationUnit | None,
) -> OrganizationUnit:
    unit, _created = OrganizationUnit.objects.get_or_create(
        name=name,
        kind=kind,
        parent=parent,
    )
    return unit


def _staff(team: OrganizationUnit) -> None:
    rows = [
        ("데모담당자01", "팀장", "042-000-0000", "demo01@example.local"),
        ("데모담당자02", "과장", "042-000-0001", "demo02@example.local"),
        ("데모담당자03", "대리", "042-000-0002", "demo03@example.local"),
        ("데모담당자04", "대리", "042-000-0003", "demo04@example.local"),
        ("데모담당자05", "주임", "042-000-0004", "demo05@example.local"),
        ("데모담당자06", "파견직", "042-000-0005", "demo06@example.local"),
    ]
    for name, position, extension, email in rows:
        StaffProfile.objects.get_or_create(
            organization=team,
            display_name=name,
            defaults={
                "position": position,
                "extension": extension,
                "email": email,
                "duty_keywords": "성과평가 ESG 혁신 평가 운영",
                "is_demo": True,
            },
        )
