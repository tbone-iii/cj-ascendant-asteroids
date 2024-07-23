from discord import Embed

from .utils import create_error_embed, create_warning_embed


def missing_permissions(error: Exception) -> Embed:
    """Missing permissions embed.

    Description: Creates an error embed for missing permissions.
    :Return: Embed
    """
    return create_error_embed(
        title="Missing Permissions!",
        description=f"You cannot run this command as you are missing the following permissions: \
            {',' .join(error.missing_permissions)}",
    )


def action_canceled() -> Embed:
    """Cancel action embed.

    Description: Creates a warning embed for canceling an action.
    :Return: Embed
    """
    return create_warning_embed(title="Action canceled")


def error_occurred() -> Embed:
    """Error embed.

    Description: Creates an error embed for an unknown error occurring.
    :Return: Embed
    """
    return create_error_embed(
        title="Error!",
        description="An error has occurred while running your command!",
    )
