from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from article_overload.exceptions import DatabaseSessionNotInitializedError

from .session_manager import DatabaseSessionManager

sessionmanager = DatabaseSessionManager()


async def get_database() -> AsyncIterator[AsyncSession]:
    """Async generator for database session."""
    if sessionmanager.session is None:
        raise DatabaseSessionNotInitializedError

    session = sessionmanager.session()
    if session is None:
        raise DatabaseSessionNotInitializedError
    try:
        yield session
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
