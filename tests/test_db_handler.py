from collections.abc import AsyncGenerator, Sequence
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest
from article_overload.db import handler, models, objects
from sqlalchemy import Engine, Row, create_engine, text

from .context import article_overload  # noqa: F401, ignore unused import
from .exceptions import InvalidTableNameError
from .utils import TEST_DIRECTORY, DatabaseSetupInfo, prebuild_article, prebuild_articles, remove_local_db_files

HandlerEngine = tuple[handler.DatabaseHandler, Engine]
SetupData = AsyncGenerator[HandlerEngine, None]
Articles = list[objects.Article]


remove_local_db_files()


def get_new_db_file_path(uuid: str) -> Path:
    """Generate a new file path for the database.

    :Return: Path to the new database file.
    """
    return (TEST_DIRECTORY / Path(f"./output/test_handler_{uuid}.db")).absolute()


def get_new_db_file_url(uuid: str) -> str:
    """Generate a new file URL for the database.

    :Return: URL to the new database file.
    """
    file_path = str(get_new_db_file_path(uuid))
    return f"sqlite+aiosqlite:///{file_path}"


def generate_db_setup_info() -> DatabaseSetupInfo:
    """Generate the database setup info for testing."""
    uuid = str(uuid4())
    return DatabaseSetupInfo(
        file_path=get_new_db_file_path(uuid),
        database_url=get_new_db_file_url(uuid),
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
async def setup_db() -> SetupData:
    """Set up databases for testing. Distinct database names will always be generated to prevent conflicts.

    :Return: Async generator yielding a tuple of the database handler and engine.
    """
    database_setup_info = generate_db_setup_info()

    engine = create_engine(database_setup_info.sync_database_url)
    database_handler = await handler.DatabaseHandler.create(database_setup_info.database_url)
    yield database_handler, engine

    # teardown database - if you wish to keep the output database, comment out the following line
    remove_local_db_files()


@pytest.mark.asyncio()
@pytest.mark.parametrize(("sentence_length"), [1, 100, 1000])
async def test_async_add_article_verify_parameter_storage_and_retrieval(
    sentence_length: int,
    setup_db: SetupData,
) -> None:
    database_handler, _ = await anext(setup_db)

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
    setup_db: SetupData,
) -> None:
    database_handler, sync_engine = await anext(setup_db)

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
    setup_db: SetupData,
) -> None:
    database_handler, sync_engine = await anext(setup_db)

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
