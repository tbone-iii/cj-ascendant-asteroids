class InvalidTokenError(Exception):
    """For when a token is invalid."""


class NoTokenProvidedError(Exception):
    """For when no token is provided."""


class ViewDoesNotExistError(Exception):
    """For when a view does not exist."""
