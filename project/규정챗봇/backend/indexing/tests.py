from indexing.services import parse_markdown_clauses


def test_parse_markdown_clauses_when_articles_and_paragraphs_exist() -> None:
    markdown = (
        "제1조(목적)\n"
        "① 이 지침은 성과평가 기준을 정한다.\n"
        "② 세부 기준은 별표를 따른다.\n"
        "제2조(평가등급)\n"
        "제1항 평가등급은 점수에 따라 산정한다.\n"
    )

    clauses = parse_markdown_clauses(markdown)

    assert len(clauses) == 3
    assert clauses[0].article == "제1조"
    assert clauses[0].paragraph == "①"
    assert "성과평가" in clauses[0].body
    assert clauses[2].article == "제2조"
    assert clauses[2].paragraph == "제1항"
