from typing import Any

from discord import (
    Embed,
    Interaction,
    User,
    app_commands,
)
from discord.ext import commands
from utils.constants import SCORE_BOARD_SPACING_SIZE

from article_overload.bot import ArticleOverloadBot
from article_overload.db.objects import Score

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

    async def get_score_text_row(self, score_object: Score) -> str:
        """Get a score in a text row."""
        username = (await self.client.fetch_user(score_object.user_id)).name.strip()

        return (
            f"`{username:<{SCORE_BOARD_SPACING_SIZE}}"
            f"{score_object.score!s:<{SCORE_BOARD_SPACING_SIZE}}"
            f"{score_object.latest_played.strftime("%B %d, %Y"):<{SCORE_BOARD_SPACING_SIZE}}`\n"
        )

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
            score_text += await self.get_score_text_row(score_object)

        embed.add_field(name=score_text, value="")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="get_user_score", description="Shows the scores of the top ten players.")
    async def get_user_score(self, interaction: Interaction, mention_target: User) -> None:
        """Bot command.

        Description: Shows the score of a player.
        :Return: None
        """
        # TODO: use get_player_score_object instead of score
        score_object = await self.client.database_handler.get_player_score(mention_target.id)

        embed = Embed(title="Scoreboard")
        embed.add_field(name=await self.get_score_text_row(score_object), value="")
        await interaction.response.send_message(embed=embed)


async def setup(client: ArticleOverloadBot) -> None:
    """Set up command.

    Description: Sets up the Scoreboard Cog
    :Return: None
    """
    await client.add_cog(ScoreboardCog(client))
