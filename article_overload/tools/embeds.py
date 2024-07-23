from discord import Embed
from discord.app_commands import MissingPermissions

from .utils import create_error_embed, create_warning_embed


def create_missing_permissions_embed(
    error: MissingPermissions,
) -> Embed:  # TODO: Review what actual error type is and where it's sourced from
    """Missing permissions embed.

    Description: Creates an error embed for missing permissions.
    :Return: Embed
    """
    missing_permissions = ",".join(error.missing_permissions)
    return create_error_embed(
        title="Missing Permissions!",
        description=f"You cannot run this command as you are missing the following permissions: {missing_permissions}",
    )


def create_action_canceled_embed() -> Embed:
    """Cancel action embed.

    Description: Creates a warning embed for canceling an action.
    :Return: Embed
    """
    return create_warning_embed(title="Action canceled")


def create_error_occurred_embed() -> Embed:
    """Error embed.

    Description: Creates an error embed for an unknown error occurring.
    :Return: Embed
    """
    return create_error_embed(
        title="Error!",
        description="An error has occurred while running your command!",
    )
