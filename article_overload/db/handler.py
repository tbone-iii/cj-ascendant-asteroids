from typing import TypeVar

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import Session

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
        self.session_factory = async_sessionmaker(self.engine)
        return self

    async def add_article(self, article: Article) -> Article:
        """Add article to database. Return the new Article.

        :Return: `Article`
        """
        async with self.session_factory() as session, session.begin():
            article_records = await session.scalars(
                insert(ArticleRecord).returning(ArticleRecord),
                [article.get_dict()],
            )
            article_record = next(article_records)
            return Article.from_dict(article_record.__dict__)

    async def add_articles(self, articles: list[Article]) -> list[Article]:
        """Add multiple articles to the database. Return the new Articles.

        This is a bulk insert operation.
        :Return: `list[Article]`
        """
        async with self.session_factory() as session, session.begin():
            article_records = await session.scalars(
                insert(ArticleRecord).returning(ArticleRecord),
                [article.get_dict() for article in articles],
            )
            return [Article.from_dict(article_record.__dict__) for article_record in article_records]

    async def get_article_by_id(self, article_id: int) -> Article | None:
        """Get article by ID.

        :Return: `Article` or `None`
        """
        async with self.session_factory() as session:
            result = await session.execute(
                select(ArticleRecord).where(ArticleRecord.id == article_id),
            )
            article_record = result.scalars().first()
            return Article.from_dict(article_record.__dict__) if article_record else None

    async def get_all_articles(self) -> list[Article]:
        """Get all articles.

        :See:
        https://docs.sqlalchemy.org/en/20/core/connections.html#sqlalchemy.engine.Row

        :Return: `list[Article]`
        """
        async with self.session_factory() as session:
            result = await session.execute(select(ArticleRecord))
            article_record_rows = result.all()
            return [
                Article.from_dict(article_record_row.ArticleRecord.__dict__)
                for article_record_row in article_record_rows
            ]

    def update_article(
        self,
        session: Session,
        article_id: int,
        article: Article,
    ) -> None:
        """Update article by ID.

        :Return: `None`
        """
        query = session.query(ArticleRecord)
        article_record = query.filter(ArticleRecord.id == article_id).first()

        if article_record is None:
            print(
                color_message(
                    message=f"Warning: Article ID '{article_id}' not found. Skipping update.",
                    color="yellow",
                ),
            )
            return

        for key, value in article.get_dict().items():
            setattr(article, key, value)

        session.commit()
