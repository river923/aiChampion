import re
from dataclasses import dataclass

from documents.models import RegulationDocument
from indexing.models import ClauseIndex


@dataclass(frozen=True, slots=True)
class ParsedClause:
    article: str
    paragraph: str
    title: str
    body: str


ARTICLE_PATTERN = re.compile(
    r"(?m)^(?:#{1,6}\s*)?(제\s*\d+\s*조(?:의\s*\d+)?)(?:\s*\(([^)]*)\))?"
)
PARAGRAPH_PATTERN = re.compile(r"(제\s*\d+\s*항|①|②|③|④|⑤|⑥|⑦|⑧|⑨|⑩)")


def rebuild_clause_index(document: RegulationDocument) -> int:
    ClauseIndex.objects.filter(document=document).delete()
    parsed_clauses = parse_markdown_clauses(document.parsed_markdown)
    rows = [
        ClauseIndex(
            document=document,
            article=clause.article,
            paragraph=clause.paragraph,
            title=clause.title,
            body=clause.body,
            keywords=f"{document.title} {clause.title} {clause.body[:500]}",
        )
        for clause in parsed_clauses
    ]
    ClauseIndex.objects.bulk_create(rows)
    return len(rows)


def parse_markdown_clauses(markdown: str) -> list[ParsedClause]:
    matches = list(ARTICLE_PATTERN.finditer(markdown))
    clauses: list[ParsedClause] = []
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        section = markdown[start:end].strip()
        article = _normalize_spaces(match.group(1))
        title = (match.group(2) or "").strip()
        clauses.extend(_split_paragraphs(article, title, section))
    return clauses


def _split_paragraphs(article: str, title: str, section: str) -> list[ParsedClause]:
    matches = list(PARAGRAPH_PATTERN.finditer(section))
    if not matches:
        return [ParsedClause(article=article, paragraph="", title=title, body=section)]
    clauses: list[ParsedClause] = []
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(section)
        body = section[start:end].strip()
        clauses.append(
            ParsedClause(
                article=article,
                paragraph=_normalize_spaces(match.group(1)),
                title=title,
                body=body,
            )
        )
    return clauses


def _normalize_spaces(value: str) -> str:
    return re.sub(r"\s+", "", value)
