from discord import Interaction, app_commands
from discord.ext import commands

from article_overload.bot import ArticleOverloadBot
from article_overload.constants import MAX_INCORRECT
from article_overload.db.objects import ArticleResponse
from article_overload.exceptions import NoSessionFoundError
from article_overload.game_classes import AbilityType, Game, Player
from article_overload.tools.desc import CommandDescriptions
from article_overload.tools.embeds import (
    create_article_embed,
    create_correct_answer_embed,
    create_incorrect_answer_embed,
    create_start_game_embed,
    create_time_up_embed,
    create_too_many_incorrect_embed,
    create_warning_embed,
)
from article_overload.views import ContinueButtonView, GameView, StartButtonView


class ArticleOverload(commands.GroupCog, group_name="article_overload", group_description="Game commmands"):
    """ArticleOverload cog class."""

    def __init__(self, client: ArticleOverloadBot) -> None:
        """Initialize method.

        Description: Initialize ArticleOverload cog as a subclass of commands.Cog
        :Return: None
        """
        self.client = client
        self.database_handler = client.database_handler

    @app_commands.command(
        name="play",
        description=CommandDescriptions.GAME_START.value,
    )
    async def article_overload(self, interaction: Interaction) -> None:
        """Bot command.

        Description: Starts the game
        :Return: None
        """
        if interaction.user.id in self.client.games:
            await interaction.response.send_message(
                embed=create_warning_embed(
                    title="Already In Game!",
                    description="You are already in a game!",
                ),
            )
            return

        # Object layer
        game = Game()
        author = interaction.user
        url = author.avatar.url if author.avatar else ""
        player = Player(
            player_id=author.id,
            name=author.name,
            display_name=author.display_name,
            avatar_url=url,
        )
        game.add_player(player)
        self.client.games.update({interaction.user.id: game})

        # UI layer
        start_button = StartButtonView(org_user=interaction.user.id)
        embed = create_start_game_embed(player)
        await interaction.response.send_message(embed=embed, view=start_button)
        await start_button.wait()

        if start_button.difficulty is None:
            await interaction.edit_original_response(
                embed=create_warning_embed(
                    title="Expired!",
                    description="You took too long to select a game difficulty",
                )
            )
            return

        msg = f"{interaction.user.name} started a game.\n"
        self.client.logger.info(msg)

        game.start_game(start_button.difficulty)
        game.start_article_timer()

        # The Sessions table in the database tracks users and scores
        session_records = await self.client.database_handler.start_new_sessions(game.player_ids)
        for player, session_record in zip(game.players, session_records, strict=False):
            game.add_session_id_for_player(player=player, session_id=session_record.id)

        while True:
            article_handler = await self.client.database_handler.get_random_article()
            embed = create_article_embed(article_handler=article_handler, player=player, game=game)

            game_view = GameView(
                interaction.user.id,
                article_handler,
                timeout=game.article_timer,
            )

            await interaction.edit_original_response(
                embed=embed,
                view=game_view,
            )
            await game_view.wait()

            game.stop_article_timer()

            if game_view.sentence is None:
                await interaction.edit_original_response(embed=create_time_up_embed(player, game), view=None)
                break

            is_correct = game_view.sentence == article_handler.false_sentence
            if is_correct:
                player.add_correct()
                embed = create_correct_answer_embed(player)
            else:
                player.add_incorrect()
                embed = create_incorrect_answer_embed(
                    player=player, highlighted_summary=article_handler.highlighted_summary
                )

            session_id = game.get_session_id_for_player(player)
            if session_id is None:
                raise NoSessionFoundError

            # The Article Responses are for player telemetry on performance
            await self.client.database_handler.add_article_response_from_article(
                article=article_handler._article,  # noqa: SLF001
                article_response=ArticleResponse(
                    user_id=player.player_id,
                    session_id=session_id,
                    response=game_view.sentence,
                    is_correct=is_correct,
                ),
            )

            if player.incorrect == MAX_INCORRECT:
                await interaction.edit_original_response(
                    embed=create_too_many_incorrect_embed(player, game),
                    view=None,
                )
                break

            continue_button = ContinueButtonView()

            await interaction.edit_original_response(embed=embed, view=continue_button)
            await continue_button.wait()

        self.client.games.pop(player.get_player_id())
        await self.notify_database_of_game_end_for_players(game, game.players)
        return

    @app_commands.command(name="end_game", description=CommandDescriptions.GAME_END.value)
    async def end_game(self, interaction: Interaction) -> None:
        """Bot command.

        Description: Ends the game
        :Return: None
        """
        game = self.client.games.get(interaction.user.id, None)
        if game is None:
            return await interaction.response.send_message(
                embed=create_warning_embed(
                    title="Not In Game!",
                    description="You are not in a game!",
                ),
            )

        game.end_game()
        await self.notify_database_of_game_end_for_players(game, game.players)
        duration = game.get_game_duration()
        self.client.games.pop(interaction.user.id)

        return await interaction.response.send_message(f"Game ended! Duration: {duration}")

    @app_commands.command(name="list_abilities", description="List all possible abilities.")
    async def list_abilities(self, interaction: Interaction) -> None:
        """Bot command to list all possible abilities."""
        abilities = [ability.value for ability in AbilityType]
        abilities_list = "\n".join(abilities)
        await interaction.response.send_message(f"Possible abilities:\n{abilities_list}")

    async def notify_database_of_game_end_for_players(self, game: Game, players: list[Player]) -> None:
        """Notify the database of the game end for all players.

        Asyncio is used here to parallelize the database calls.

        :Return: None
        """
        session_ids = [
            session_id for player in players if (session_id := game.get_session_id_for_player(player)) is not None
        ]
        scores = [player.get_score() for player in players]
        await self.database_handler.end_sessions(session_ids=session_ids, scores=scores)


async def setup(client: ArticleOverloadBot) -> None:
    """Set up command.

    Description: Sets up the ArticleOverload Cog
    :Return: None
    """
    await client.add_cog(ArticleOverload(client))
