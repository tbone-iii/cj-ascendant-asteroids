import inspect
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from article_overload.exceptions import DatabaseSessionNotInitializedError

from .session_manager import DatabaseSessionManager

sessionmanager = DatabaseSessionManager()


def get_class_parameters(cls: type | object) -> list[str]:
    """Get the parameters of a class.

    Description: Force the class to be a type if it is an object instance.

    :Return: `list[str]`
    """
    if isinstance(cls, object):
        cls = type(cls)

    parameters_map = inspect.signature(cls).parameters
    return list(parameters_map.keys())


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
