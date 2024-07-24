from asyncio import current_task

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)

from article_overload.exceptions import (
    DatabaseEngineNotInitializedError,
    DatabaseSessionNotInitializedError,
)


class DatabaseSessionManager:
    """Database session manager class."""

    def __init__(self) -> None:
        self.engine: AsyncEngine | None = None
        self.session_maker: async_sessionmaker | None = None
        self.session: async_scoped_session | None = None

    def init_db(self, database_url: str) -> None:
        """Initialize the async database session."""
        self.engine = create_async_engine(database_url)

        if self.engine is None:
            raise DatabaseEngineNotInitializedError

        self.session_maker = async_sessionmaker(self.engine)
        self.session = async_scoped_session(self.session_maker, scopefunc=current_task)

    async def close(self) -> None:
        """Close the database session."""
        if self.engine is None:
            raise DatabaseSessionNotInitializedError
        await self.engine.dispose()
