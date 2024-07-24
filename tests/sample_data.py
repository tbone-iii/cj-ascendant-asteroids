from article_overload.db import objects

from .context import article_overload  # noqa: F401

sample_articles = [
    objects.Article(
        id=1,
        url="https://example1.com",
        body_text="This is a short body text. It is two sentences long.",
        summary="Example summary, emojis may be included. 😊",
    ),
    objects.Article(
        id=2,
        url="https://example2.com",
        body_text="This is a long body text. " * 100,
        summary="Example summary. " * 100,
    ),
    objects.Article(
        id=3,
        url="https://example3.com",
        body_text="This is a long body text. " * 1000,
        summary="Example summary. " * 1000,
    ),
    objects.Article(
        id=99,
        url="https://differentsite-100.xyz",
        body_text="Body. " * 50,
        summary="The summary is longer than the body because AI is smart.",
    ),
]
