import sqlite3
from collections.abc import AsyncGenerator, Sequence
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest
from article_overload.db import handler, models, objects
from sqlalchemy import Engine, Row, create_engine, text

from .exceptions import InvalidTableNameError
from .sample_data import sample_articles
from .utils import (
    TEST_DIRECTORY,
    DatabaseSetupInfo,
    prebuild_article,
    prebuild_articles,
    remove_local_db_files,
)

HandlerEngine = tuple[handler.DatabaseHandler, Engine]
SetupData = AsyncGenerator[HandlerEngine, None]
Articles = list[objects.Article]


remove_local_db_files()


def get_new_db_file_path(identifier: str) -> Path:
    """Generate a new file path for the database.

    :Return: Path to the new database file.
    """
    return (TEST_DIRECTORY / Path(f"./output/test_handler_{identifier}.db")).absolute()


def get_new_db_file_url(identifier: str) -> str:
    """Generate a new file URL for the database.

    :Return: URL to the new database file.
    """
    file_path = str(get_new_db_file_path(identifier))
    return f"sqlite+aiosqlite:///{file_path}"


def generate_db_setup_info() -> DatabaseSetupInfo:
    """Generate the database setup info for testing."""
    identifier = str(uuid4())
    return DatabaseSetupInfo(
        file_path=get_new_db_file_path(identifier),
        database_url=get_new_db_file_url(identifier),
    )


def read_all_article_rows_sync(engine: Engine, table_name: str) -> Sequence[Row[Any]]:
    """Read all rows from the article table, given the article table name.

    :Return: All rows from the article table.
    """
    # To prevent any risk of SQL injection attacks if somehow this function is used somewhere else
    if not table_name.isalnum():
        raise InvalidTableNameError

    query_string = text(f"SELECT id, url, body_text, summary FROM {table_name} ORDER BY id ASC")  # noqa: S608
    with engine.connect() as connection:
        result = connection.execute(query_string)
        return result.fetchall()


@pytest.fixture()
async def setup_blank_db() -> SetupData:
    """Set up databases for testing. Distinct database names will always be generated to prevent conflicts.

    :Return: Async generator yielding a tuple of the database handler and engine.
    """
    database_setup_info = generate_db_setup_info()

    engine = create_engine(database_setup_info.sync_database_url)
    database_handler = await handler.DatabaseHandler.create(database_setup_info.database_url)
    yield database_handler, engine

    # teardown database - if you wish to keep the output database, comment out the following line
    database_setup_info.file_path.unlink()


@pytest.fixture()
def setup_sample_db_file() -> DatabaseSetupInfo:
    """Set up a sample database for testing that is prepopulated with data.

    :Return: Database setup information, which includes the database url and file path.
    """
    # sample_art

    database_setup_info = generate_db_setup_info()

    table_name = models.ArticleRecord.__tablename__
    # To prevent any risk of SQL injection attacks if somehow this test gets out to prod
    if not table_name.isalnum():
        raise InvalidTableNameError

    with sqlite3.connect(database_setup_info.file_path) as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY,
                url TEXT,
                body_text TEXT,
                summary TEXT
            )
        """)

        for article in sample_articles:
            cursor.execute(
                f"""
                INSERT INTO {table_name} (id, url, body_text, summary) VALUES (?, ?, ?, ?)
            """,  # noqa: S608, no string injection risk here
                (article.id, article.url, article.body_text, article.summary),
            )

    return database_setup_info


@pytest.mark.asyncio()
@pytest.mark.parametrize(("sentence_length"), [1, 100, 1000])
async def test_async_add_article_verify_parameter_storage_and_retrieval(
    sentence_length: int,
    setup_blank_db: SetupData,
) -> None:
    database_handler, _ = await anext(setup_blank_db)

    article = prebuild_article(sentence_length)
    returned_article = await database_handler.add_article(article)

    assert returned_article is not None
    assert returned_article.id == 1
    assert returned_article.body_text == article.body_text
    assert returned_article.url == article.url
    assert returned_article.summary == article.summary


@pytest.mark.asyncio()
@pytest.mark.parametrize(
    ("sentence_length", "article_quantity"),
    [(1, 1), (100, 10), (1000, 100)],
)
async def test_async_add_multiple_articles_one_by_one_verify_by_reading_database_synchronously(
    sentence_length: int,
    article_quantity: int,
    setup_blank_db: SetupData,
) -> None:
    database_handler, sync_engine = await anext(setup_blank_db)

    prebuilt_articles = prebuild_articles(
        sentence_length=sentence_length,
        article_quantity=article_quantity,
    )
    for article in prebuilt_articles:
        await database_handler.add_article(article)

    # Testing portion to verify the data in the database
    # Pulling the data via synchronous method to ensure data is stored correctly
    records = read_all_article_rows_sync(engine=sync_engine, table_name=models.ArticleRecord.__tablename__)
    assert len(records) == len(prebuilt_articles)

    for article, row in zip(prebuilt_articles, records, strict=True):
        assert row.url == article.url
        assert row.body_text == article.body_text
        assert row.summary == article.summary


@pytest.mark.asyncio()
@pytest.mark.parametrize(
    ("sentence_length", "article_quantity"),
    [(1, 1), (100, 10), (1000, 100)],
)
async def test_async_bulk_insert_multiple_articles_verify_by_reading_database_synchronously(
    sentence_length: int,
    article_quantity: int,
    setup_blank_db: SetupData,
) -> None:
    database_handler, sync_engine = await anext(setup_blank_db)

    prebuilt_articles = prebuild_articles(
        sentence_length=sentence_length,
        article_quantity=article_quantity,
    )
    await database_handler.add_articles(prebuilt_articles)

    # Testing portion to verify the data in the database
    # Pulling the data via synchronous method to ensure data is stored correctly
    records = read_all_article_rows_sync(engine=sync_engine, table_name=models.ArticleRecord.__tablename__)

    assert len(records) == len(prebuilt_articles)

    for article, row in zip(prebuilt_articles, records, strict=True):
        assert row.url == article.url
        assert row.body_text == article.body_text
        assert row.summary == article.summary


@pytest.mark.asyncio()
@pytest.mark.parametrize("article", sample_articles)
async def test_get_article_by_id_from_sample_db(
    article: objects.Article,
    setup_sample_db_file: DatabaseSetupInfo,
) -> None:
    database_handler = await handler.DatabaseHandler.create(setup_sample_db_file.database_url)

    assert article.id is not None, "Sanity check."
    retrieved_article = await database_handler.get_article_by_id(article.id)

    assert retrieved_article == article


@pytest.mark.asyncio()
async def test_get_all_articles_from_sample_db(
    setup_sample_db_file: DatabaseSetupInfo,
) -> None:
    database_handler = await handler.DatabaseHandler.create(setup_sample_db_file.database_url)
    retrieved_articles = await database_handler.get_all_articles()

    assert retrieved_articles == sample_articles
