import subprocess
import tempfile
from pathlib import Path

from django.db import transaction

from documents.models import RegulationDocument
from indexing.services import rebuild_clause_index


def parse_document(document: RegulationDocument) -> int:
    source_path = Path(document.source_file.path)
    try:
        markdown = _run_kordoc(source_path)
    except subprocess.SubprocessError as exc:
        document.status = RegulationDocument.Status.FAILED
        document.parse_error = "kordoc 변환에 실패했습니다."
        document.save(update_fields=["status", "parse_error", "updated_at"])
        raise DocumentParseError(document_id=document.pk, message=str(exc)) from exc
    with transaction.atomic():
        document.parsed_markdown = markdown
        document.status = RegulationDocument.Status.PARSED
        document.parse_error = ""
        document.save(update_fields=["parsed_markdown", "status", "parse_error", "updated_at"])
        return rebuild_clause_index(document)


def _run_kordoc(source_path: Path) -> str:
    with tempfile.TemporaryDirectory() as output_dir:
        subprocess.run(
            ["npx", "-y", "kordoc@latest", "--silent", "-d", output_dir, str(source_path)],
            check=True,
            capture_output=True,
            text=True,
            timeout=120,
        )
        markdown_files = sorted(Path(output_dir).glob("*.md"))
        if not markdown_files:
            raise subprocess.SubprocessError("kordoc markdown output not found")
        return markdown_files[0].read_text(encoding="utf-8")


class DocumentParseError(Exception):
    def __init__(self, document_id: int | None, message: str) -> None:
        super().__init__(message)
        self.document_id = document_id
