from collections.abc import AsyncGenerator
from dataclasses import dataclass
from pathlib import Path

from article_overload.db import handler, objects
from sqlalchemy import Engine

HandlerEngine = tuple[handler.DatabaseHandler, Engine]
SetupData = AsyncGenerator[HandlerEngine, None]
Articles = list[objects.Article]


TEST_DIRECTORY = Path("./tests/").resolve()
OUTPUT_DIRECTORY = TEST_DIRECTORY / "output/"


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
    for file_path in OUTPUT_DIRECTORY.glob("*.db"):
        file_path.unlink()
