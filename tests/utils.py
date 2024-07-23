from collections.abc import AsyncGenerator
from dataclasses import dataclass
from pathlib import Path

from article_overload.db import handler, objects
from sqlalchemy import Engine

HandlerEngine = tuple[handler.DatabaseHandler, Engine]
SetupData = AsyncGenerator[HandlerEngine, None]
Articles = list[objects.Article]


TEST_DIRECTORY = Path("./tests/").resolve()


@dataclass
class DatabaseSetupInfo:
    """Dataclass to store database setup information for the tests."""

    file_path: Path
    database_url: str

    @property
    def sync_database_url(self) -> str:
        """Return the synchronous database URL."""
        return self.database_url.replace("aiosqlite", "pysqlite")


def remove_local_db_files() -> None:
    """Remove all local database files created during testing."""
    for file_path in TEST_DIRECTORY.glob("*.db"):
        file_path.unlink()


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
