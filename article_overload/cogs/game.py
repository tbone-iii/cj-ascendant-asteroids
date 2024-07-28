from discord import Interaction, app_commands
from discord.ext import commands

from article_overload.bot import ArticleOverloadBot
from article_overload.constants import MAX_INCORRECT, ImageURLs
from article_overload.db.handler import DatabaseHandler
from article_overload.db.objects import ArticleResponse
from article_overload.exceptions import NoSessionFoundError
from article_overload.game_classes import AbilityType, Game, Player
from article_overload.log import our_logger
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
        if self.is_existing_game_player(interaction):
            await send_already_in_game_message(interaction)
            return

        # Setup
        game, player = self.setup_game_and_player(interaction)
        our_logger.info(f"Game object initialized for '{interaction.user.name}'")

        # Setup game menu
        start_button = await self.initialize_menu(interaction, player=player)
        if start_button.start_timer_seconds is None:
            await self.send_game_expired_message(interaction)
            return

        # Begin game
        begin_game(game, interaction, start_timer_seconds=start_button.start_timer_seconds)

        # The Sessions table in the database tracks users and scores
        await initialize_sessions_table(database_handler=self.database_handler, game=game)

        our_logger.info(f"Game loop started for '{interaction.user.name}'")
        flag = True
        while flag:
            flag = await self.main_game_loop(
                game=game,
                interaction=interaction,
                database_handler=self.database_handler,
            )

        # End game
        for player in game.players:
            self.client.games.pop(player.get_player_id())
            our_logger.info(f"Game loop ended for '{interaction.user.name}'")

        await self.notify_database_of_game_end_for_players(game, game.players)
        return

    @app_commands.command(name="end_game", description=CommandDescriptions.GAME_END.value)
    async def end_game(self, interaction: Interaction) -> None:
        """Bot command.

        Description: Ends the game
        :Return: None
        """
        game = self.client.games.pop(interaction.user.id)
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

    def is_existing_game_player(self, interaction: Interaction) -> bool:
        """Check if the user is already in a game.

        Description: Checks if the user is already in a game.
        :Return: `bool`
        """
        return interaction.user.id in self.client.games

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

    def setup_game_and_player(self, interaction: Interaction) -> tuple[Game, Player]:
        """Set up the game and player.

        Description: Sets up the game and player objects.
        :Return: `tuple[Game, Player]`
        """
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
        return game, player

    async def initialize_menu(self, interaction: Interaction, player: Player) -> StartButtonView:
        """Initialize the start game menu.

        :Return: `StartButtonView`
        """
        start_button = StartButtonView(user_id=interaction.user.id)

        score = await self.database_handler.get_player_score(player.player_id)
        player.all_time_score = score.score

        embed = create_start_game_embed(player)
        await interaction.response.send_message(embed=embed, view=start_button)
        await start_button.wait()

        our_logger.info(f"Start button initialized for '{interaction.user.name}'")
        return start_button

    async def send_game_expired_message(self, interaction: Interaction) -> None:
        """Say the game expired.

        Description: Sends a message that the game has expired.
        :Return: None
        """
        our_logger.info(f"Game difficulty not selected for '{interaction.user.name}'")
        await interaction.edit_original_response(
            embed=create_warning_embed(
                title="Expired!",
                description="You took too long to select a game difficulty",
            )
        )

    async def main_game_loop(self, game: Game, interaction: Interaction, database_handler: DatabaseHandler) -> bool:
        """Run the main game loop.

        Description: Main game loop for the ArticleOverload game.
        :Return: flag to continue the game
        """
        article_handler = await database_handler.get_random_article()

        player = game.players[0]  # TODO: Change this to be dynamic for PvP
        embed = create_article_embed(article_handler=article_handler, player=player, game=game)

        game_view = GameView(
            interaction.user.id,
            article_handler,
            timeout=game.article_timer * 0.75,
            player=player
        )

        await game_view.create_ability_buttons(org_interaction=interaction)
        await interaction.edit_original_response(
            embed=embed,
            view=game_view,
        )
        player.async_loop_abilities_meter.start()
        await game_view.wait()

        game.stop_article_timer()

        if game_view.sentence is None:
            game_view = GameView(
                interaction.user.id, article_handler=article_handler, timeout=game.article_timer * 0.25, player=player
            )
            embed.set_image(url=ImageURLs.HURRY)
            await interaction.edit_original_response(embed=embed, view=game_view)
            await game_view.wait()

        if game_view.sentence is None:
            await interaction.edit_original_response(embed=create_time_up_embed(player, game), view=None)
            return False

        is_correct = game_view.sentence == article_handler.false_sentence
        if is_correct:
            player.add_correct()
            embed = create_correct_answer_embed(player)
            our_logger.info(f"Correct answer for '{interaction.user.name}'")
        else:
            player.add_incorrect()
            embed = create_incorrect_answer_embed(
                player=player, highlighted_summary=article_handler.highlighted_summary
            )
            our_logger.info(f"Incorrect answer for '{interaction.user.name}'")

        session_id = game.get_session_id_for_player(player)
        if session_id is None:
            raise NoSessionFoundError

        # The Article Responses are for player telemetry on performance
        article_response = ArticleResponse(
            user_id=player.player_id,
            session_id=session_id,
            response=game_view.sentence.text,
            is_correct=is_correct,
        )
        # TODO: replace _article with article_handler, change underlying db handler functions too
        await database_handler.add_article_response_from_article(
            article=article_handler._article,  # noqa: SLF001
            article_response=article_response,
        )
        our_logger.info(f"Article response {article_response} added for '{interaction.user.name}'")

        if player.incorrect == MAX_INCORRECT:
            our_logger.info(f"Too many incorrect answers for '{interaction.user.name}'")
            await interaction.edit_original_response(
                embed=create_too_many_incorrect_embed(player, game),
                view=None,
            )
            return False

        continue_button = ContinueButtonView()

        await interaction.edit_original_response(embed=embed, view=continue_button)
        await continue_button.wait()

        return True


def check_user_submission(interaction: Interaction, org_interaction: Interaction, game_view: GameView) -> bool:
    """Check if the user submission is valid."""
    return interaction.user.id == org_interaction.user.id and game_view.sentence is not None


async def setup(client: ArticleOverloadBot) -> None:
    """Set up command.

    Description: Sets up the ArticleOverload Cog
    :Return: None
    """
    await client.add_cog(ArticleOverload(client))


def begin_game(game: Game, interaction: Interaction, start_timer_seconds: float) -> None:
    """Begin the game.

    Description: Begins the game.
    :Return: None
    """
    game.start_game(start_timer_seconds)
    game.start_article_timer()
    our_logger.info(f"'{interaction.user.name}' started a game.\n")


async def initialize_sessions_table(database_handler: DatabaseHandler, game: Game) -> None:
    """Initialize the sessions table for all players in the game.

    Description: Initializes the sessions table.
    :Return: None
    """
    session_records = await database_handler.start_new_sessions(game.player_ids)
    for player, session_record in zip(game.players, session_records, strict=False):
        game.add_session_id_for_player(player=player, session_id=session_record.id)
        our_logger.info(f"Session record {session_record} added for '{player.name}'")


async def send_already_in_game_message(interaction: Interaction) -> None:
    """Send a message that the user is already in a game.

    Description: Sends a message that the user is already in a game.
    :Return: None
    """
    await interaction.response.send_message(
        embed=create_warning_embed(
            title="Already In Game!",
            description="You are already in a game!",
        ),
    )
