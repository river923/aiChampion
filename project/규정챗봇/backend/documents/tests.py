from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from documents.models import validate_supported_document


def test_validate_supported_document_when_extension_is_not_allowed() -> None:
    uploaded = SimpleUploadedFile("manual.docx", b"demo")

    try:
        validate_supported_document(uploaded)
    except ValidationError as exc:
        assert ".hwp, .hwpx, .pdf" in str(exc)
    else:
        raise AssertionError("미지원 확장자는 거부되어야 합니다.")


def test_validate_supported_document_when_extension_is_allowed() -> None:
    uploaded = SimpleUploadedFile("manual.hwpx", b"demo")

    validate_supported_document(uploaded)
