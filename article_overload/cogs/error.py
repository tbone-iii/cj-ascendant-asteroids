from discord import Interaction
from discord.app_commands import AppCommandError, MissingPermissions
from discord.ext import commands

from article_overload.bot import ArticleOverloadBot
from article_overload.tools.embeds import (
    create_error_occurred_embed,
    create_missing_permissions_embed,
)


class Error(commands.Cog):
    """Error cog class."""

    def __init__(self, client: ArticleOverloadBot) -> None:
        """Initialize method.

        Description: Initialize commands.Cog subclass.
        :Return: None
        """
        self.client = client

    @commands.Cog.listener("on_app_command_error")
    async def on_app_command_error(
        self,
        interaction: Interaction,
        error: AppCommandError,
    ) -> None:
        """Error Listener.

        Description: Catches errors and returns a proper response
        :Return: None
        """
        if isinstance(error, MissingPermissions):
            await interaction.response.send_message(
                embed=create_missing_permissions_embed(error=error),
            )

        else:
            await interaction.response.send_message(embed=create_error_occurred_embed())

        raise error


async def setup(client: ArticleOverloadBot) -> None:
    """Set up command.

    Description: Sets up the Error Cog
    :Return: None
    """
    await client.add_cog(Error(client))
