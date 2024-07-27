from datetime import UTC, datetime
from itertools import cycle

from article_overload.db.models import ArticleRecord, ArticleResponseRecord, QuestionRecord, SessionRecord, SizeRecord
from article_overload.db.objects import Article

from .context import article_overload  # noqa: F401


def prebuild_article(sentence_length: int) -> Article:
    """Prebuild articles for testing.

    The sentence length parameter is used to extend the length of the body text and summary.

    :Return: Prebuilt article object
    """
    body_text_multiplier = 100
    return Article(
        url="https://example.com",
        body_text="This is a short body text. It is two sentences long." * body_text_multiplier,
        summary="A new car. A new house. A new chair." * sentence_length,
        questions=["A new car.", "A new dinosaur.", "A new house.", "A new chair."],
        incorrect_option_index=1,
        title="Example Title",
        topic="General",
        size="Small",
        author="Author",
        date_published=datetime(2021, 1, 1, tzinfo=UTC),
    )


def prebuild_articles(sentence_length: int, article_quantity: int) -> list[Article]:
    """Prebuild articles for testing.

    The sentence length parameter is used to extend the length of the body text and summary.

    :Return: Prebuilt article object
    """
    size_generator = cycle(["Small", "Medium", "Large"])
    return [
        Article(
            url=f"https://example{index}.com",
            body_text=f"This is a long body text. {index}" * sentence_length,
            summary=f"A new car. A new house. A new chair. {index}" * sentence_length,
            questions=["A new car.", f"A new dinosaur. {index}", "A new house.", "A new chair."],
            incorrect_option_index=1,
            title=f"Example Title {index}",
            topic="General {index}",
            size=next(size_generator),
            author=f"Author {index}",
            date_published=datetime(2021, 1, 1, tzinfo=UTC),
        )
        for index in range(article_quantity)
    ]


sample_articles = [
    Article(
        id=1,
        url="https://example1.com",
        body_text="This is a short body text. It is two sentences long.",
        summary="A new car. A new house. A new chair.",
        questions=["Fact A", "Fact B", "Fact C", "Fake Fact"],
        incorrect_option_index=3,
        title="Example Title",
        topic="General",
        size="Small",
        author="Author",
        date_published=datetime(2005, 4, 20, tzinfo=UTC),
    ),
    Article(
        id=None,
        url="https://example2.com",
        body_text="This is a long body text. " * 100,
        summary="A new car. A new house. A new chair.",
        questions=["Fact A", "Fake Fact", "Fact C", "Fact D"],
        incorrect_option_index=1,
        title="Example Title",
        topic="Sports",
        size="Large",
        author="Author",
        date_published=datetime(2021, 3, 3, tzinfo=UTC),
    ),
]

sample_true_statements = [
    ["Fact A", "Fact B", "Fact C"],
    ["Fact A", "Fact C", "Fact D"],
]

sample_false_statements = [
    "Fake Fact",
    "Fake Fact",
]

sample_size_records = [
    SizeRecord(id=1, size="Small"),
    SizeRecord(id=2, size="Medium"),
    SizeRecord(id=3, size="Large"),
]

sample_questions_records = [
    [
        QuestionRecord(id=1, article_id=1001, question="Fact A"),
        QuestionRecord(id=2, article_id=1001, question="Fact B"),
    ],
    [
        QuestionRecord(id=3, article_id=1002, question="apple"),
        QuestionRecord(id=4, article_id=1002, question="banana"),
        QuestionRecord(id=5, article_id=1002, question="cherry"),
        QuestionRecord(id=6, article_id=1002, question="dog"),
    ],
]

expected_global_ratio_correct_values = [
    0.5,
    1.0,
]

sample_session_records = [
    SessionRecord(
        id=1,
        user_id=1234567890,
        start_date=datetime(2021, 1, 1, hour=10, minute=15, second=12, tzinfo=UTC),
        end_date=datetime(2021, 1, 1, hour=10, minute=15, second=12, tzinfo=UTC),
        score=0,
    ),
    SessionRecord(
        id=2,
        user_id=9876543210,
        start_date=datetime(2021, 1, 1, hour=11, minute=12, second=5, tzinfo=UTC),
        end_date=datetime(2021, 1, 1, hour=11, minute=12, second=5, tzinfo=UTC),
        score=0,
    ),
]

sample_article_responses_records = [
    [
        ArticleResponseRecord(
            id=1,
            article_id=1001,
            user_id=1234567890,
            session_id=1,
            response="Fact A",
            correct=False,
            answered_on=datetime(2021, 1, 1, hour=10, minute=15, second=12, tzinfo=UTC),
        ),
        ArticleResponseRecord(
            id=3,
            article_id=1001,
            user_id=9876543210,
            session_id=2,
            response="Fake Fact",
            correct=True,
            answered_on=datetime(2021, 1, 1, hour=11, minute=12, second=6, tzinfo=UTC),
        ),
    ],
    [
        ArticleResponseRecord(
            id=2,
            article_id=1002,
            user_id=1234567890,
            session_id=1,
            response="Fake Fact",
            correct=True,
            answered_on=datetime(2021, 1, 1, hour=11, minute=12, second=5, tzinfo=UTC),
        ),
        ArticleResponseRecord(
            id=4,
            article_id=1002,
            user_id=9876543210,
            session_id=2,
            response="Fake Fact",
            correct=True,
            answered_on=datetime(2021, 1, 1, hour=11, minute=13, second=19, tzinfo=UTC),
        ),
    ],
]

sample_article_records = [
    ArticleRecord(
        id=1001,
        url="https://example1.com",
        body_text="This is a short body text. It is two sentences long.",
        summary="A new car. A new house. A new chair.",
        questions=sample_questions_records[0],
        incorrect_option_index=1,
        title="Example Title",
        author="Author",
        date_published=datetime(2005, 4, 20, tzinfo=UTC),
        topic="General",
        size_id=1,
        article_responses=sample_article_responses_records[0],
    ),
    ArticleRecord(
        id=1002,
        url="https://example2.com",
        body_text="This is a long body text. " * 100,
        summary="A new apple. A new banana. A new cherry. A new dog.",
        questions=sample_questions_records[1],
        incorrect_option_index=3,
        title="Example Title",
        author="Author",
        date_published=datetime(2021, 3, 3, tzinfo=UTC),
        topic="Sports",
        size_id=2,
        article_responses=sample_article_responses_records[1],
    ),
]
