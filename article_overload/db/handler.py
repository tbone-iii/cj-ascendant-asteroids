from collections.abc import Sequence
from typing import TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from sqlalchemy.sql.expression import func

from article_overload.exceptions import NoArticlesFoundError, SizeRecordNotFoundError

from .models import ArticleRecord, QuestionRecord, SizeRecord, init_database
from .objects import Article

T = TypeVar("T")


class DatabaseHandler:
    """Asynchronous database handler class.

    Session management is handled by the `with_session` decorator.
    """

    def __init__(self, database_url: str) -> None:
        self.database_url = database_url
        self.engine: AsyncEngine
        self.session_factory: async_sessionmaker[AsyncSession]

    @classmethod
    async def create(cls, database_url: str) -> "DatabaseHandler":
        """Create a new instance of the DatabaseHandler.

        :Return: `DatabaseHandler`
        """
        self = cls(database_url)
        self.engine = await init_database(database_url)
        self.session_factory = async_sessionmaker(self.engine, expire_on_commit=False)
        return self

    async def get_size_record_by_size(self, size: str, session: AsyncSession) -> SizeRecord:
        """Get size record by size.

        If it doesn't exist, create a new entry to the database and return it.

        :Return: `SizeRecord` or `None`
        """
        result = await session.execute(select(SizeRecord).where(SizeRecord.size == size))
        size_record = result.scalars().first()

        if size_record is None:
            size_record = SizeRecord(size=size)
            session.add(size_record)
            await session.flush()
        return size_record

    async def add_article(self, article: Article) -> Article:
        """Add `Article` to database. Return the updated `Article`.

        :Return: `Article`
        """
        # parse down Article summary and fake_fact

        async with self.session_factory() as session:
            async with session.begin():
                size_record = await self.get_size_record_by_size(article.size, session)
                article_record = article.create_article_record(size_record)
                session.add(article_record)

            return article.update_id_from_article_record(article_record)

    async def add_articles(self, articles: list[Article]) -> list[Article]:
        """Add multiple articles to the database. Return the new Articles.

        This is a bulk insert operation.
        :Return: `list[Article]`
        """
        async with self.session_factory() as session:
            async with session.begin():
                size_records = [await self.get_size_record_by_size(article.size, session) for article in articles]
                article_records = [
                    article.create_article_record(size_record)
                    for article, size_record in zip(articles, size_records, strict=False)
                ]
                session.add_all(article_records)

            return [
                article.update_id_from_article_record(article_record)
                for article, article_record in zip(articles, article_records, strict=False)
            ]

    async def get_article_by_id(self, article_id: int) -> Article | None:
        """Get `Article` by ID.

        :Return: `Article` or `None`
        """
        async with self.session_factory() as session:
            article_record = await session.get(ArticleRecord, article_id)

            if article_record is None:
                return None

            question_records = await self.get_question_records_from_article_record(article_record, session)
            size_record = await self.get_size_records_from_article_record(article_record, session)

            return Article.create_from_article_record(
                article_record=article_record,
                question_records=list(question_records),
                size_record=size_record,
            )

    @staticmethod
    async def get_question_records_from_article_record(
        article_record: ArticleRecord,
        session: AsyncSession,
    ) -> Sequence[QuestionRecord]:
        """Get question record from article record.

        :Return: `list[QuestionRecord]`
        """
        result = await session.execute(article_record.questions.select())
        return result.scalars().all()

    @staticmethod
    async def get_size_records_from_article_record(article_record: ArticleRecord, session: AsyncSession) -> SizeRecord:
        """Get size record from article records.

        :Return: `SizeRecord` or `None`
        """
        size_record = await session.get(SizeRecord, article_record.size_id)
        if size_record is None:
            raise SizeRecordNotFoundError

        return size_record

    async def get_all_articles(self) -> list[Article]:
        """Get all articles.

        :See:
        https://docs.sqlalchemy.org/en/20/core/connections.html#sqlalchemy.engine.Row

        :Return: `list[Article]`
        """
        async with self.session_factory() as session:
            result = await session.execute(select(ArticleRecord))
            article_records = result.scalars().all()
            questions_records = [
                await self.get_question_records_from_article_record(article_record, session)
                for article_record in article_records
            ]
            size_records = [
                await self.get_size_records_from_article_record(article_record, session)
                for article_record in article_records
            ]

            return [
                Article.create_from_article_record(
                    article_record=article_record,
                    question_records=list(question_records),
                    size_record=size_record,
                )
                for article_record, question_records, size_record in zip(
                    article_records,
                    questions_records,
                    size_records,
                    strict=True,
                )
            ]

    async def get_random_article(self) -> Article:
        """Get a random article.

        :Return: `Article`
        """
        async with self.session_factory() as session:
            result = await session.execute(select(ArticleRecord).order_by(func.random()).limit(1))
            article_record = result.scalars().first()

            if article_record is None:
                raise NoArticlesFoundError

            question_records = await self.get_question_records_from_article_record(article_record, session)
            size_record = await self.get_size_records_from_article_record(article_record, session)

            return Article.create_from_article_record(
                article_record=article_record,
                question_records=list(question_records),
                size_record=size_record,
            )
