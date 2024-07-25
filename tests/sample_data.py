from article_overload.db import objects

from .context import article_overload  # noqa: F401


def prebuild_article(sentence_length: int) -> objects.Article:
    """Prebuild articles for testing.

    The sentence length parameter is used to extend the length of the body text and summary.

    :Return: Prebuilt article object
    """
    return objects.Article(
        url="https://example.com",
        body_text="This is a short body text. It is two sentences long." * sentence_length,
        summary="Example summary, emojis may be included. 😊" * sentence_length,
    )


def prebuild_articles(sentence_length: int, article_quantity: int) -> list[objects.Article]:
    """Prebuild articles for testing.

    The sentence length parameter is used to extend the length of the body text and summary.

    :Return: Prebuilt article object
    """
    return [
        objects.Article(
            url=f"https://example{index}.com",
            body_text=f"{index}: This is a long body text. " * sentence_length,
            summary=f"{index}: Example summary. " * sentence_length,
        )
        for index in range(article_quantity)
    ]


sample_articles = [
    objects.Article(
        id=1001,
        url="https://example1.com",
        body_text="This is a short body text. It is two sentences long.",
        summary="Example summary, emojis may be included. 😊",
    ),
    objects.Article(
        id=None,
        url="https://example2.com",
        body_text="This is a long body text. " * 100,
        summary="Example summary. " * 100,
    ),
    objects.Article(
        id=None,
        url="https://example3.com",
        body_text="This is a long body text. " * 1000,
        summary="Example summary. " * 1000,
    ),
    objects.Article(
        id=None,
        url="https://differentsite-100.xyz",
        body_text="Body. " * 50,
        summary="The summary is longer than the body because AI is smart.",
    ),
]

sample_article_records = [
    objects.ArticleRecord(
        id=1001,
        url="https://example1.com",
        body_text="This is a short body text. It is two sentences long.",
        summary="Example summary, emojis may be included. 😊",
    ),
    objects.ArticleRecord(
        id=1002,
        url="https://example2.com",
        body_text="This is a long body text. " * 100,
        summary="Example summary. " * 100,
    ),
    objects.ArticleRecord(
        id=1003,
        url="https://example3.com",
        body_text="This is a long body text. " * 1000,
        summary="Example summary. " * 1000,
    ),
    objects.ArticleRecord(
        id=1004,
        url="https://differentsite-100.xyz",
        body_text="Body. " * 50,
        summary="The summary is longer than the body because AI is smart.",
    ),
]
