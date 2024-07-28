import itertools as it
import logging
import sqlite3
from collections.abc import AsyncGenerator, Sequence
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest
from article_overload.db import handler, models, objects
from sqlalchemy import Engine, Row, create_engine, text

from .exceptions import InvalidTableNameError
from .sample_data import (
    expected_global_ratio_correct_values,
    expected_scores,
    prebuild_article,
    prebuild_articles,
    sample_article_records,
    sample_article_responses_records,
    sample_questions_records,
    sample_session_records,
    sample_size_records,
)
from .sqlalchemy_log import sqlalchemy_logger
from .utils import (
    TEST_DIRECTORY,
    DatabaseSetupInfo,
    remove_local_db_files,
)

sqlalchemy_logger.setLevel(logging.DEBUG)

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


def read_all_article_rows_sync(engine: Engine) -> Sequence[Row[Any]]:
    """Read all rows from the article table, given the article table name.

    :Return: All rows from the article table.
    """
    # To prevent any risk of SQL injection attacks if somehow this function is used somewhere else
    table_name = models.ArticleRecord.__tablename__
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

    engine = create_engine(database_setup_info.sync_database_url, echo=False)
    database_handler = await handler.DatabaseHandler.create(database_setup_info.database_url)
    yield database_handler, engine

    # teardown database - if you wish to keep the output database, comment out the following line
    database_setup_info.file_path.unlink()


@pytest.fixture()
def setup_sample_db_file() -> DatabaseSetupInfo:
    """Set up a sample database for testing that is prepopulated with data.

    The structure is HIGHLY important for the tests to work correctly.
    Refer to `ArticleRecord` in `models.py` for the structure.

    :Return: Database setup information, which includes the database url and file path.
    """
    # sample_art

    database_setup_info = generate_db_setup_info()

    article_table_name = models.ArticleRecord.__tablename__
    questions_table_name = models.QuestionRecord.__tablename__
    size_table_name = models.SizeRecord.__tablename__
    article_response_table_name = models.ArticleResponseRecord.__tablename__
    session_table_name = models.SessionRecord.__tablename__

    table_names = [
        article_table_name,
        questions_table_name,
        size_table_name,
        article_response_table_name,
        session_table_name,
    ]

    # To prevent any risk of SQL injection attacks if somehow this test gets out to prod

    for table_name in table_names:
        if not table_name.isalnum():
            raise InvalidTableNameError

    with sqlite3.connect(database_setup_info.file_path) as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {article_table_name} (
                id INTEGER PRIMARY KEY NOT NULL,
                url TEXT NOT NULL,
                body_text TEXT NOT NULL,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                incorrect_option_index INTEGER NOT NULL,
                summary TEXT NOT NULL,
                date_published DATETIME,
                topic TEXT,
                size_id INTEGER NOT NULL
            );""")

        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {questions_table_name} (
                id INTEGER PRIMARY KEY NOT NULL,
                article_id INTEGER NOT NULL,
                question TEXT NOT NULL
            );""")

        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {size_table_name} (
                id INTEGER PRIMARY KEY NOT NULL,
                size TEXT NOT NULL
            );
        """)

        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {article_response_table_name} (
                id INTEGER PRIMARY KEY NOT NULL,
                article_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                session_id INTEGER NOT NULL,
                response TEXT NOT NULL,
                correct BOOLEAN NOT NULL,
                answered_on DATETIME NOT NULL
            );
        """)

        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {session_table_name} (
                id INTEGER PRIMARY KEY NOT NULL,
                user_id INTEGER NOT NULL,
                start_date DATETIME NOT NULL,
                end_date DATETIME NOT NULL,
                score INTEGER NOT NULL
            );
        """)

        for article in sample_article_records:
            cursor.execute(
                f"""
                INSERT INTO {article_table_name}
                (
                    id,
                    url,
                    body_text,
                    title,
                    author,
                    incorrect_option_index,
                    summary,
                    date_published,
                    topic,
                    size_id
                )

                VALUES

                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
                (
                    article.id,
                    article.url,
                    article.body_text,
                    article.title,
                    article.author,
                    article.incorrect_option_index,
                    article.summary,
                    article.date_published,
                    article.topic,
                    article.size_id,
                ),
            )

        for question_record in it.chain(*sample_questions_records):
            cursor.execute(
                f"""
                    INSERT INTO {questions_table_name}
                    (id, article_id, question) VALUES (?, ?, ?);
                """,  # noqa: S608, no risk of SQL injection
                (question_record.id, question_record.article_id, question_record.question),
            )

        for size_record in sample_size_records:
            cursor.execute(
                f"""
                    INSERT INTO {size_table_name}
                    (id, size) VALUES (?, ?);
                """,  # noqa: S608, no risk of SQL injection
                (size_record.id, size_record.size),
            )

        for article_response_records, session_record in zip(
            sample_article_responses_records,
            sample_session_records,
            strict=True,
        ):
            for article_response_record in article_response_records:
                cursor.execute(
                    f"""
                        INSERT INTO {article_response_table_name}
                        (id, article_id, user_id, session_id, response, correct, answered_on)
                        VALUES
                        (?, ?, ?, ?, ?, ?, ?);
                    """,
                    (
                        article_response_record.id,
                        article_response_record.article_id,
                        article_response_record.user_id,
                        session_record.id,
                        article_response_record.response,
                        article_response_record.correct,
                        article_response_record.answered_on,
                    ),
                )

        for session_record in sample_session_records:
            cursor.execute(
                f"""
                    INSERT INTO {session_table_name}
                    (id, user_id, start_date, end_date, score)
                    VALUES
                    (?, ?, ?, ?, ?);
                """,
                (
                    session_record.id,
                    session_record.user_id,
                    session_record.start_date,
                    session_record.end_date,
                    session_record.score,
                ),
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
    records = read_all_article_rows_sync(engine=sync_engine)
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
    records = read_all_article_rows_sync(engine=sync_engine)

    assert len(records) == len(prebuilt_articles)

    for article, row in zip(prebuilt_articles, records, strict=True):
        assert row.url == article.url
        assert row.body_text == article.body_text
        assert row.summary == article.summary


@pytest.mark.asyncio()
@pytest.mark.parametrize("article_record", sample_article_records)
async def test_get_article_by_id_from_sample_db(
    article_record: models.ArticleRecord,
    setup_sample_db_file: DatabaseSetupInfo,
) -> None:
    database_handler = await handler.DatabaseHandler.create(setup_sample_db_file.database_url)

    assert article_record.id is not None, "Sanity check."
    retrieved_article = await database_handler.get_article_by_id(article_record.id)

    assert retrieved_article is not None
    assert retrieved_article.id == article_record.id


@pytest.mark.asyncio()
async def test_get_all_articles_from_sample_db(
    setup_sample_db_file: DatabaseSetupInfo,
) -> None:
    database_handler = await handler.DatabaseHandler.create(setup_sample_db_file.database_url)
    retrieved_articles = await database_handler.get_all_articles()

    expected_ids = [article.id for article in sample_article_records]
    retrieved_ids = [article.id for article in retrieved_articles]
    assert expected_ids == retrieved_ids


@pytest.mark.asyncio()
async def test_get_random_article_from_sample_db(
    setup_sample_db_file: DatabaseSetupInfo,
) -> None:
    database_handler = await handler.DatabaseHandler.create(setup_sample_db_file.database_url)
    retrieved_article = await database_handler.get_random_article()

    assert retrieved_article is not None
    assert retrieved_article.id is not None
    assert retrieved_article.id in [article.id for article in sample_article_records]


@pytest.mark.asyncio()
@pytest.mark.parametrize(
    (
        "article_record",
        "question_records",
        "expected_ratio",
    ),
    zip(
        sample_article_records,
        sample_questions_records,
        expected_global_ratio_correct_values,
        strict=True,
    ),
)
async def test_get_global_ratio_correct_on_article(
    setup_sample_db_file: DatabaseSetupInfo,
    article_record: models.ArticleRecord,
    question_records: list[models.QuestionRecord],
    expected_ratio: float,
) -> None:
    database_handler = await handler.DatabaseHandler.create(setup_sample_db_file.database_url)

    article = objects.Article.create_from_article_record(
        article_record=article_record,
        question_records=question_records,
        size_record=sample_size_records[article_record.size_id - 1],
    )
    ratio = await database_handler.get_global_ratio_correct_on_article(article)
    assert ratio is not None
    assert round(ratio, 2) == round(expected_ratio, 2)


@pytest.mark.asyncio()
async def test_add_article_response_to_sample_db(
    setup_sample_db_file: DatabaseSetupInfo,
) -> None:
    database_handler = await handler.DatabaseHandler.create(setup_sample_db_file.database_url)

    article = objects.Article.create_from_article_record(
        article_record=sample_article_records[0],
        question_records=sample_questions_records[0],
        size_record=sample_size_records[0],
    )

    article_response = objects.ArticleResponse(
        user_id=999999999,
        session_id=1,
        is_correct=False,
        response="Fact B",
    )
    article_response_record = await database_handler.add_article_response_from_article(article, article_response)
    assert article_response_record.id is not None


@pytest.mark.asyncio()
async def test_start_session_and_update_session_score(
    setup_sample_db_file: DatabaseSetupInfo,
) -> None:
    score = 10
    database_handler = await handler.DatabaseHandler.create(setup_sample_db_file.database_url)

    session_record: models.SessionRecord = await database_handler.start_new_session(user_id=999999999)
    assert session_record.id is not None

    session_record = await database_handler.end_session(session_record.id, score=score)
    assert session_record.score == score


@pytest.mark.asyncio()
async def test_get_existing_player_score_from_sample_db(
    setup_sample_db_file: DatabaseSetupInfo,
) -> None:
    database_handler = await handler.DatabaseHandler.create(setup_sample_db_file.database_url)

    user_id = 1234567890
    expected_score = 40

    score = await database_handler.get_player_score(user_id)
    assert score == expected_score


@pytest.mark.asyncio()
async def test_get_nonexistent_player_score_from_sample_db(
    setup_sample_db_file: DatabaseSetupInfo,
) -> None:
    database_handler = await handler.DatabaseHandler.create(setup_sample_db_file.database_url)

    user_id = 1111111111
    expected_score = 0

    score = await database_handler.get_player_score(user_id)
    assert score == expected_score


@pytest.mark.asyncio()
async def test_get_top_n_scores_from_sample_db(
    setup_sample_db_file: DatabaseSetupInfo,
) -> None:
    database_handler = await handler.DatabaseHandler.create(setup_sample_db_file.database_url)

    n = 10
    top_scores: list[objects.Score] = await database_handler.get_top_n_scores(n=n)

    assert top_scores == expected_scores


@pytest.mark.asyncio()
async def test_get_player_player_topic_stat(setup_sample_db_file: DatabaseSetupInfo) -> None:
    database_handler = await handler.DatabaseHandler.create(setup_sample_db_file.database_url)
    user_id = 1234567890

    user_topic_stat = await database_handler.get_player_topic_stat(user_id)

    assert user_topic_stat == objects.UserTopicStat(
        total_correct=1,
        total_responses=4,
        topic=None,
        user_id=user_id,
    )


@pytest.mark.asyncio()
async def test_get_player_topic_stat_by_topic_that_exists(setup_sample_db_file: DatabaseSetupInfo) -> None:
    database_handler = await handler.DatabaseHandler.create(setup_sample_db_file.database_url)
    user_id = 1234567890

    topic = "Sports"
    user_topic_stat = await database_handler.get_player_topic_stat(user_id, topic=topic)
    assert user_topic_stat == objects.UserTopicStat(
        total_correct=1,
        total_responses=2,
        topic=topic,
        user_id=user_id,
    )


@pytest.mark.asyncio()
async def test_get_player_topic_stat_by_topic_that_does_not_exist(setup_sample_db_file: DatabaseSetupInfo) -> None:
    database_handler = await handler.DatabaseHandler.create(setup_sample_db_file.database_url)
    user_id = 1234567890

    user_topic_stat = await database_handler.get_player_topic_stat(user_id, topic="Insane Topic!")

    assert user_topic_stat == objects.UserTopicStat(
        total_correct=0,
        total_responses=0,
        topic="Insane Topic!",
        user_id=user_id,
    )


@pytest.mark.asyncio()
async def test_get_player_topics_order(
    setup_sample_db_file: DatabaseSetupInfo,
) -> None:
    database_handler = await handler.DatabaseHandler.create(setup_sample_db_file.database_url)

    user_id = 1234567890
    expected_topics = [
        objects.UserTopicStat(
            total_correct=1,
            total_responses=2,
            topic="Sports",
            user_id=user_id,
        ),
        objects.UserTopicStat(
            total_correct=0,
            total_responses=1,
            topic="Entertainment",
            user_id=user_id,
        ),
        objects.UserTopicStat(
            total_correct=0,
            total_responses=1,
            topic="General",
            user_id=user_id,
        ),
    ]

    user_topic_stats = await database_handler.get_player_topic_stats_in_order(user_id)
    assert user_topic_stats == expected_topics
