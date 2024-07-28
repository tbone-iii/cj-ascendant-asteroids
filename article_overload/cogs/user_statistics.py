from typing import Any

from discord import (
    Embed,
    Interaction,
    User,
    app_commands,
)
from discord.ext import commands

from article_overload.bot import ArticleOverloadBot
from article_overload.constants import (
    SCORE_BOARD_COLOR,
    SCORE_BOARD_NUM_SCORES_TO_SHOW,
    SCORE_BOARD_SPACING_SIZE,
    ImageURLs,
)
from article_overload.db.objects import UserTopicStat

InteractionChannel = Any


class UserStatsCog(commands.GroupCog, group_name="view", group_description="View statistics about Article Overload"):
    """User statistics cog class."""

    def __init__(self, client: ArticleOverloadBot) -> None:
        """Initialize method.

        Description Initialize commands.Cog subclass.
        :Return: None
        """
        self.client = client
        self.database_handler = client.database_handler

    @app_commands.command(
        name="leaderboard",
        description=f"Shows the scores of the top {SCORE_BOARD_NUM_SCORES_TO_SHOW} players.",
    )
    async def leaderboard(self, interaction: Interaction) -> None:
        """Bot command.

        Description: Shows the scores of the top ten players.
        :Return: None
        """
        embed = Embed(title="Scoreboard", color=SCORE_BOARD_COLOR)

        header_text = (
            f"`{_left_padded_text("Name", SCORE_BOARD_SPACING_SIZE)}"
            f"{_left_padded_text("Score", SCORE_BOARD_SPACING_SIZE)}"
            f"{_left_padded_text("Last Seen", SCORE_BOARD_SPACING_SIZE)}`\n"
        )

        score_text = ""
        player_scores = await self.client.database_handler.get_top_n_scores(n=SCORE_BOARD_NUM_SCORES_TO_SHOW)
        for score_object in player_scores:
            user = await self.client.fetch_user(score_object.user_id)
            score_text += (
                f"`{_left_padded_text(user.name, SCORE_BOARD_SPACING_SIZE)}"
                f"{_left_padded_text(str(score_object.score), SCORE_BOARD_SPACING_SIZE)}"
                f"{_left_padded_text(score_object.latest_played_formatted, SCORE_BOARD_SPACING_SIZE)}`\n"
            )

        embed.add_field(name=header_text, value="")
        embed.add_field(name="", value=score_text, inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="player", description="Shows the user stats overview.")
    async def player(self, interaction: Interaction, mention_target: User) -> None:
        """Bot command. Shows the user stats overview.

        :Return: None
        """
        user_id = mention_target.id

        player_score = await self.client.database_handler.get_player_score(user_id)
        overall_topic_stat = await self.client.database_handler.get_player_topic_stat(user_id)
        player_topic_stats_breakdown = await self.client.database_handler.get_player_topic_stats_in_order(user_id)

        # Strings need to be formatted cleanly for the embed value
        overall_topic_title = f"Overall Score - {player_score.score}"
        overall_topic_string = _make_topic_string(overall_topic_stat)

        if len(player_topic_stats_breakdown) > 0:
            topic_stat = player_topic_stats_breakdown[0]
            best_topic_string = _make_topic_string(topic_stat)

            topic_stat = player_topic_stats_breakdown[-1]
            worst_topic_string = _make_topic_string(topic_stat)

        else:
            best_topic_string = "`<None>`"
            worst_topic_string = "`<None>`"

        embed = (
            Embed(title="User Stats Overview", color=SCORE_BOARD_COLOR)
            .set_thumbnail(url=ImageURLs.ANIMATED_TROPHY)
            .add_field(name=overall_topic_title, value=overall_topic_string)
            .add_field(name="Best Topic", value=best_topic_string, inline=False)
            .add_field(name="Worst Topic", value=worst_topic_string, inline=True)
        )
        await interaction.response.send_message(embed=embed)


def _left_padded_text(text: str, padding_size: int) -> str:
    return f"{text:<{padding_size}}"


def _make_topic_string(topic_stat: UserTopicStat) -> str:
    topic = topic_stat.topic
    if topic is None:
        topic = "<All Topics>"

    return f"`{topic}` - {topic_stat.total_correct}/{topic_stat.total_responses} [{topic_stat.percentage_correct}%]"


async def setup(client: ArticleOverloadBot) -> None:
    """Set up command.

    Description: Sets up the Scoreboard Cog
    :Return: None
    """
    await client.add_cog(UserStatsCog(client))
