from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CitationDetail:
    title: str
    body: str


@dataclass(frozen=True, slots=True)
class AnswerResult:
    status: str
    answer: str
    citations: list[CitationDetail]
    error_message: str = ""


@dataclass(frozen=True, slots=True)
class ParsedCitation:
    document_title: str
    article: str
    paragraph: str = ""
    appendix: str = ""


@dataclass(frozen=True, slots=True)
class ParsedContact:
    department: str
    name: str
    position: str
    extension: str
    reason: str


@dataclass(frozen=True, slots=True)
class ParsedLLMAnswer:
    answer: str
    citations: list[ParsedCitation]
    contact: ParsedContact | None
    confidence: str
    missing_evidence_reason: str
