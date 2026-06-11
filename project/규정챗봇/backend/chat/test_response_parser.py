from chat.response_parser import parse_llm_answer


def test_parse_llm_answer_when_response_is_wrapped_in_markdown_fence() -> None:
    content = (
        "```json\n"
        "{\n"
        '  "answer": "성과평가지침 제1조를 기준으로 판단합니다.",\n'
        '  "citations": [\n'
        "    {\n"
        '      "document_title": "성과평가지침",\n'
        '      "article": "제1조",\n'
        '      "paragraph": "제1항"\n'
        "    }\n"
        "  ],\n"
        '  "confidence": "high"\n'
        "}\n"
        "```"
    )

    parsed = parse_llm_answer(content)

    assert parsed.answer == "성과평가지침 제1조를 기준으로 판단합니다."
    assert len(parsed.citations) == 1
    assert parsed.citations[0].document_title == "성과평가지침"
    assert parsed.citations[0].article == "제1조"
