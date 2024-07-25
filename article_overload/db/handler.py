from typing import TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from tools.utils import color_message

from .models import ArticleRecord, init_database
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

    async def add_article(self, article: Article) -> Article:
        """Add `Article` to database. Return the updated `Article`.

        :Return: `Article`
        """
        # parse down Article summary and fake_fact

        async with self.session_factory() as session:
            async with session.begin():
                article_record = article.create_article_record()
                session.add(article_record)

            return article.update_id_from_article_record(article_record)

    async def add_articles(self, articles: list[Article]) -> list[Article]:
        """Add multiple articles to the database. Return the new Articles.

        This is a bulk insert operation.
        :Return: `list[Article]`
        """
        async with self.session_factory() as session:
            async with session.begin():
                article_records = [article.create_article_record() for article in articles]
                session.add_all(article_records)

            return [
                article.update_id_from_article_record(article_record)
                for article, article_record in zip(articles, article_records, strict=False)
            ]

    async def get_article_by_id(self, article_id: int) -> Article | None:
        """Get article by ID.

        :Return: `Article` or `None`
        """
        async with self.session_factory() as session:
            article_record = await session.get(ArticleRecord, article_id)

            if article_record is None:
                return None
            return Article.create_from_article_record(article_record)

    async def get_all_articles(self) -> list[Article]:
        """Get all articles.

        :See:
        https://docs.sqlalchemy.org/en/20/core/connections.html#sqlalchemy.engine.Row

        :Return: `list[Article]`
        """
        async with self.session_factory() as session:
            article_records_chunked_iterator = await session.execute(select(ArticleRecord))
            article_records_tuples = article_records_chunked_iterator.all()
            article_records = [record[0] for record in article_records_tuples]
            return [Article.create_from_article_record(article_record) for article_record in article_records]
