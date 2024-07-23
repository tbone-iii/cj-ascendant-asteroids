from discord import Interaction
from discord.app_commands import MissingPermissions
from discord.ext import commands

from article_overload.bot import ArticleOverloadBot
from article_overload.tools.embeds import error_occurred, missing_permissions


class Error(commands.Cog):
    """Error cog class."""

    def __init__(self, client: ArticleOverloadBot) -> None:
        """Initialize method.

        Description: Initialize commands.Cog subclass.
        :Return: None
        """
        self.client = client

    @commands.Cog.listener()
    async def on_application_command_error(
        self,
        interaction: Interaction,
        error: Exception,
    ) -> None:
        """Error Listener.

        Description: Catches errors and returns a proper response
        :Return: None
        """
        if isinstance(error, MissingPermissions):
            await interaction.response.send_message(
                embed=missing_permissions(error=error),
            )

        else:
            await interaction.response.send_message(embed=error_occurred())

        raise error


async def setup(client: ArticleOverloadBot) -> None:
    """Sets up command.

    Description: Sets up the Error Cog
    :Return: None
    """
    await client.add_cog(Error(client))
