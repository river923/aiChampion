import re
import unicodedata

from chat.types import CitationDetail, ParsedLLMAnswer
from indexing.models import ClauseIndex


def citation_text(clause: ClauseIndex) -> str:
    if clause.title:
        return f"[{clause.document.title} {clause.article}({clause.title})]"
    return f"[{clause.document.title} {clause.article}]"


def collect_valid_citations(parsed_answer: ParsedLLMAnswer, clauses: list[ClauseIndex]) -> list[CitationDetail]:
    returned_citations: list[CitationDetail] = []
    seen_titles: set[str] = set()
    for parsed_citation in parsed_answer.citations:
        doc_title = unicodedata.normalize("NFC", parsed_citation.document_title.strip())
        article = unicodedata.normalize("NFC", parsed_citation.article.strip())
        matched_clause = _matching_clause(doc_title, article, clauses)
        if matched_clause is not None:
            title = citation_text(matched_clause)
            if title not in seen_titles:
                returned_citations.append(CitationDetail(title=title, body=matched_clause.body))
                seen_titles.add(title)
            continue
        fallback = _fallback_citation_title(doc_title, article, parsed_citation.paragraph)
        if fallback and fallback not in seen_titles:
            returned_citations.append(
                CitationDetail(title=fallback, body="전문 내용을 제공할 수 없는 임의의 인용입니다.")
            )
            seen_titles.add(fallback)
    return returned_citations


def _matching_clause(doc_title: str, article: str, clauses: list[ClauseIndex]) -> ClauseIndex | None:
    for clause in clauses:
        db_doc_title = unicodedata.normalize("NFC", clause.document.title)
        db_article = unicodedata.normalize("NFC", clause.article)
        doc_match = db_doc_title in doc_title or doc_title in db_doc_title
        if doc_match and _article_matches(db_article, article):
            return clause
    return None


def _article_matches(db_article: str, article: str) -> bool:
    valid_nums = re.findall(r"\d+", db_article)
    llm_nums = re.findall(r"\d+", article)
    if valid_nums and valid_nums[0] in llm_nums:
        return True
    return db_article in article or article in db_article


def _fallback_citation_title(doc_title: str, article: str, paragraph: str) -> str:
    if not doc_title:
        return ""
    title = f"{doc_title} {article}".strip()
    if paragraph:
        title = f"{title} {paragraph}"
    return title
