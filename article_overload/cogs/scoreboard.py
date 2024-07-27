from typing import Any

from discord import (
    Embed,
    Interaction,
    app_commands,
)
from discord.ext import commands
from utils.constants import SCORE_BOARD_SPACING_SIZE

from article_overload.bot import ArticleOverloadBot

InteractionChannel = Any


class ScoreboardCog(commands.Cog):
    """Scoreboard cog class."""

    def __init__(self, client: ArticleOverloadBot) -> None:
        """Initialize method.

        Description Initialize commands.Cog subclass.
        :Return: None
        """
        self.client = client
        self.database_handler = client.database_handler

    @app_commands.command(name="show_scoreboard", description="Shows the scores of the top ten players.")
    async def show_scoreboard(self, interaction: Interaction) -> None:
        """Bot command.

        Description: Shows the scores of the top ten players.
        :Return: None
        """
        embed = Embed(title="Scoreboard")
        score_text = ""

        score_text += (
            f"`{"Name":<{SCORE_BOARD_SPACING_SIZE}}"
            f"{"Score":<{SCORE_BOARD_SPACING_SIZE}}"
            f"{"Date":<{SCORE_BOARD_SPACING_SIZE}}`\n"
        )

        player_scores = await self.client.database_handler.get_top_n_scores(10)
        for score_object in player_scores:
            username = (await self.client.fetch_user(score_object.user_id)).name.strip()
            score_text += (
                f"`{username:<{SCORE_BOARD_SPACING_SIZE}}"
                f"{score_object.score!s:<{SCORE_BOARD_SPACING_SIZE}}"
                f"{score_object.latest_played.strftime("%B %d, %Y"):<{SCORE_BOARD_SPACING_SIZE}}`\n"
            )

        embed.add_field(name=score_text, value="")

        await interaction.response.send_message(embed=embed)


async def setup(client: ArticleOverloadBot) -> None:
    """Set up command.

    Description: Sets up the Scoreboard Cog
    :Return: None
    """
    await client.add_cog(ScoreboardCog(client))
