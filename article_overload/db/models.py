from enum import Enum

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncEngine, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class TableName(Enum):
    """Enumeration of table names for SQLAlchemy ORM."""

    ARTICLE = "article"
    SUMMARY = "summary"
    FAKE_FACT = "fake_fact"


class Base(AsyncAttrs, DeclarativeBase):
    """Base class for SQLAlchemy ORM models."""


class ArticleRecord(Base):
    """Article model for SQLAlchemy ORM.

    Includes details like URL and summary.
    """

    __tablename__ = TableName.ARTICLE.value
    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    url: Mapped[str] = mapped_column(nullable=False)
    body_text: Mapped[str] = mapped_column(nullable=False)
    summary: Mapped[str] = mapped_column(nullable=False)


class SummaryRecord(Base):
    """Summary model for SQLAlchemy ORM.

    Includes details like the summary text and the article ID.
    """

    __tablename__ = TableName.SUMMARY.value
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    article_id = Column(Integer, ForeignKey("article.id"), nullable=False)
    summary = Column(String, nullable=False)


class FakeFactRecord(Base):
    """Fake Fact model for SQLAlchemy ORM.

    Includes details like the fake fact text and the article ID.
    """

    __tablename__ = TableName.FAKE_FACT.value
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    article_id = Column(Integer, ForeignKey("article.id"), nullable=False)
    fake_fact = Column(String, nullable=False)


async def init_database(database_url: str) -> AsyncEngine:
    """Initialize database with SQLAlchemy ORM.

    :Return: `sqlalchemy.Engine`
    """
    engine = create_async_engine(database_url, echo=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    return engine
