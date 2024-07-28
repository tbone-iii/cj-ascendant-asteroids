from typing import Any

from discord import (
    DiscordException,
    Interaction,
    StageChannel,
    TextChannel,
    Thread,
    VoiceChannel,
    app_commands,
)
from discord.ext import commands

from article_overload.bot import ArticleOverloadBot

InteractionChannel = Any


class Moderation(commands.Cog):
    """Moderation cog class."""

    def __init__(self, client: ArticleOverloadBot) -> None:
        """Initialize method.

        Description Initialize commands.Cog subclass.
        :Return: None
        """
        self.client = client
        self.database_handler = client.database_handler

    @app_commands.command(name="purge_msgs", description="Delete bot messages")
    async def purge_msgs(self, interaction: Interaction) -> None:
        """Delete bot messages from channel."""
        await interaction.response.defer()

        # Check if the interaction channel is a valid channel type for purging
        if not isinstance(interaction.channel, VoiceChannel | StageChannel | TextChannel | Thread):
            raise DiscordException

        await interaction.channel.purge(limit=100, check=lambda msg: msg.author.bot)


async def setup(client: ArticleOverloadBot) -> None:
    """Set up command.

    Description: Sets up the Sample Cog
    :Return: None
    """
    await client.add_cog(Moderation(client))
