from itertools import batched
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
from article_overload.views import PaginationView

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
        size = SCORE_BOARD_SPACING_SIZE + 3
        header_text = (
            f"`{_left_padded_text("Name", size)}"
            f"{_left_padded_text("Score", size)}"
            f"{_left_padded_text("Last Seen", size)}`\n"
        )

        data: list[dict[str, Any]] = []

        player_scores = await self.client.database_handler.get_top_n_scores(n=SCORE_BOARD_NUM_SCORES_TO_SHOW)

        stat_embedses = []
        batch_size = 4
        for score_objects in batched(player_scores, batch_size):
            embed = Embed()
            embed.add_field(name="Leaderboard", value=header_text)
            stat_embedses.append(embed)
            string = ""
            for score_object in score_objects:
                name = (await self.client.fetch_user(score_object.user_id)).name
                string += (
                    f"`{_left_padded_text(name, size)}"
                    f"{_left_padded_text(str(score_object.score), size)}"
                    f"{_left_padded_text(score_object.latest_played_formatted, size)}`\n"
                )
            embed.add_field(
                name="",
                value=string,
                inline=False,
            )

        image_embedses = []
        for score_objects in batched(player_scores, batch_size):
            embeds = []
            for score_object in score_objects:
                user = await self.client.fetch_user(score_object.user_id)
                embed.set_image(url=user.avatar.url if user.avatar else user.default_avatar)
                embeds.append(embed)
            image_embedses.append(embeds)

        for index, mega_embeds in enumerate(zip(stat_embedses, image_embedses, strict=True)):
            stat_embeds, image_embeds = mega_embeds
            embeds = [stat_embeds, *image_embeds]
            data.append({"title": f"Page {index + 1}", "description": "Click to view", "num": index, "embed": embeds})

        await interaction.response.send_message(
            embed=embed,
            view=PaginationView(org_user=interaction.user.id, data=data, page_size=4),
        )

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
