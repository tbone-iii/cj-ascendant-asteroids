from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncEngine, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, WriteOnlyMapped, mapped_column, relationship


@dataclass(frozen=True)
class TableName:
    """Enumeration of table names for SQLAlchemy ORM."""

    ARTICLE = "article"
    QUESTION = "question"
    SIZE = "size"
    ARTICLE_RESPONSE = "article_response"
    USER = "user"
    SESSION = "session"


class Base(AsyncAttrs, DeclarativeBase):
    """Base class for SQLAlchemy ORM models."""


class ArticleRecord(Base):
    """Article model for SQLAlchemy ORM.

    Includes details like URL and summary.
    """

    __tablename__ = TableName.ARTICLE
    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    url: Mapped[str] = mapped_column(nullable=False)
    body_text: Mapped[str] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    author: Mapped[str] = mapped_column(nullable=False)
    incorrect_option_index: Mapped[int] = mapped_column(nullable=False)
    summary: Mapped[str] = mapped_column(nullable=False)
    date_published: Mapped[datetime]
    topic: Mapped[str]
    questions: WriteOnlyMapped["QuestionRecord"] = relationship(
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    size_id: Mapped[int] = mapped_column(ForeignKey(f"{TableName.SIZE}.id"), nullable=False)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, url={self.url})"


class QuestionRecord(Base):
    """Summary model for SQLAlchemy ORM.

    Includes details like the summary text and the article ID.
    """

    __tablename__ = TableName.QUESTION
    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    article_id: Mapped[int] = mapped_column(ForeignKey(f"{TableName.ARTICLE}.id"), nullable=False)
    question: Mapped[str] = mapped_column(nullable=False)


class SizeRecord(Base):
    """Size model for SQLAlchemy ORM.

    Includes details like the size of the article. These are categories like "small", "medium", or "large".
    """

    __tablename__ = TableName.SIZE
    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    size: Mapped[str] = mapped_column(nullable=False, unique=True)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, size={self.size})"


async def init_database(database_url: str) -> AsyncEngine:
    """Initialize database with SQLAlchemy ORM.

    :Return: `sqlalchemy.Engine`
    """
    engine = create_async_engine(database_url, echo=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    return engine
