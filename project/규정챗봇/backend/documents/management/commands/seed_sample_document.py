from pathlib import Path
from unicodedata import normalize

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from characters.models import AICharacter
from documents.models import RegulationDocument
from documents.services import parse_document


class Command(BaseCommand):
    help = "성과평가지침 샘플 문서를 이평가 캐릭터에 연결하고 파싱합니다."

    def handle(self, *args: str, **options: str) -> None:
        character = AICharacter.objects.filter(name="이평가").first()
        if character is None:
            raise CommandError("이평가 캐릭터가 없습니다. seed_demo_org를 먼저 실행하세요.")
        raw_dir = Path(settings.PROJECT_DIR) / "data" / "raw"
        candidates = sorted(
            path
            for path in raw_dir.glob("*.hwp")
            if "성과평가지침" in normalize("NFC", path.name)
        )
        if not candidates:
            raise CommandError("성과평가지침 HWP 샘플 파일을 찾을 수 없습니다.")
        source_path = candidates[0]
        document = RegulationDocument.objects.filter(
            character=character,
            title="성과평가지침",
        ).first()
        if document is None:
            with source_path.open("rb") as source_file:
                document = RegulationDocument.objects.create(
                    character=character,
                    title="성과평가지침",
                    revision_date=timezone.datetime(2026, 3, 16).date(),
                    source_file=File(source_file, name=source_path.name),
                )
        clause_count = parse_document(document)
        self.stdout.write(
            self.style.SUCCESS(f"성과평가지침 샘플 문서와 {clause_count}개 조항을 생성했습니다.")
        )
