import pytest
from article_overload.db.items.sentence import Sentence
from article_overload.db.items.sentence_type import SentenceType


@pytest.mark.parametrize(
    ("text", "number", "expected"),
    [
        ("This is a test sentence.", 1, "`1. This is a test sentence.`"),
        ("This is a test sentence.", None, "This is a test sentence."),
    ],
)
def test_formatted_sentence_hidden_sentence_type_neutral(text: str, number: int | None, expected: str) -> None:
    sentence = Sentence(text, SentenceType.NEUTRAL)
    assert sentence.formatted_sentence_hidden(number) == expected


@pytest.mark.parametrize(
    ("text", "number", "expected"),
    [
        ("This is a test sentence.", 1, "`1. This is a test sentence.`"),
        ("This is a test sentence.", None, "This is a test sentence."),
    ],
)
def test_formatted_sentence_hidden_sentence_type_true(text: str, number: int | None, expected: str) -> None:
    sentence = Sentence(text, SentenceType.TRUE)
    assert sentence.formatted_sentence_hidden(number) == expected


def test_formatted_sentence_result_sentence_type_true() -> None:
    sentence = Sentence("This is a test sentence.", SentenceType.TRUE)
    assert sentence.formatted_sentence_result(1) == "**`1. This is a test sentence.`**"


def test_formatted_sentence_result_sentence_type_false() -> None:
    sentence = Sentence("This is a test sentence.", SentenceType.FALSE)
    assert sentence.formatted_sentence_result(1) == "~~`1. This is a test sentence.`~~"


def test_formatted_sentence_result_sentence_type_neutral() -> None:
    test_sentence = "This is a test sentence."
    sentence = Sentence(test_sentence, SentenceType.NEUTRAL)
    assert sentence.formatted_sentence_result() == test_sentence
