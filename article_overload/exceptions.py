class InvalidTokenError(Exception):
    """For when a token is invalid."""


class NoTokenProvidedError(Exception):
    """For when no token is provided."""


class ViewDoesNotExistError(Exception):
    """For when a view does not exist."""


class DatabaseEngineNotInitializedError(Exception):
    """For when the database engine is not initialized."""


class DatabaseSessionNotInitializedError(Exception):
    """For when the database session is not initialized."""


class DatabaseObjectNotProperlyInitializedError(Exception):
    """For when the database object is not properly initialized."""


class SizeRecordNotFoundError(Exception):
    """For when a size record is not found."""


class NoArticlesFoundError(Exception):
    """For when no articles are found."""


class NoSessionFoundError(Exception):
    """For when no session is found."""


class PlayerNotFoundError(Exception):
    """For when a player is not found."""


class PaginationViewMissingButtonsError(Exception):
    """For when a pagination view is missing buttons."""


class DatabaseError(Exception):
    """For when a database error occurs."""
