import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncEngine, create_async_engine


class Base(AsyncAttrs, orm.DeclarativeBase):
    """Base class for SQLAlchemy ORM models."""


class ArticleRecord(Base):
    """Article model for SQLAlchemy ORM.

    Includes details like URL and summary.
    """

    __tablename__ = "article"
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, nullable=False)
    url = sa.Column(sa.String, nullable=False)
    body_text = sa.Column(sa.String, nullable=False)
    summary = sa.Column(sa.String, nullable=False)


async def init_database(database_url: str) -> AsyncEngine:
    """Initialize database with SQLAlchemy ORM.

    :Return: `sqlalchemy.Engine`
    """
    engine = create_async_engine(database_url, echo=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    return engine
