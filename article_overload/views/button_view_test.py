import time

from discord import ButtonStyle, Interaction
from discord.ui import Button, View, button
from utils.constants import DifficultyTimer
from utils.game_classes import Game

from article_overload.bot import ArticleOverloadBot
from article_overload.tools.embeds import create_article_embed

from .game_view import GameView


class ButtonView(View):
    """Creates a view subclass containing buttons and their callback functions.

    Note: Whenever this view is created, all of the buttons get created with it.
          Perhaps theres a way to improve modularity of view/button creation, but
          for now this is what we've got. If you have any ideas, let them be known!

    """

    @button(label="Button", style=ButtonStyle.blurple)
    async def callback(self, interaction: Interaction, _: Button) -> None:
        """Responds to button interaction."""
        await interaction.response.send_message(content="Button clicked")


class StartButtonView(View):
    """View subclass containing a start button."""

    def __init__(self, og_interaction: Interaction, game: Game, client: ArticleOverloadBot) -> None:
        super().__init__()
        self.og_interaction = og_interaction
        self.game = game
        self.client = client

    @button(label="Easy", style=ButtonStyle.green)
    async def easy_callback(self, interaction: Interaction, _: Button) -> None:
        """Responds to button interaction.

        Description: Callback function for the button initialized by decorator.
        """
        await self.difficulty_callback(interaction=interaction, difficulty=DifficultyTimer.EASY)

    @button(label="Medium", style=ButtonStyle.blurple)
    async def medium_callback(self, interaction: Interaction, _: Button) -> None:
        """Responds to button interaction.

        description: callback function for the button initialized by decorator.
        """
        await self.difficulty_callback(interaction=interaction, difficulty=DifficultyTimer.MEDIUM)

    @button(label="Hard", style=ButtonStyle.red)
    async def hard_callback(self, interaction: Interaction, _: Button) -> None:
        """Responds to button interaction.

        description: callback function for the button initialized by decorator.
        """
        await self.difficulty_callback(interaction=interaction, difficulty=DifficultyTimer.HARD)

    async def difficulty_callback(self, interaction: Interaction, difficulty: DifficultyTimer) -> None:
        """Responds to button interaction.

        description: callback function for the button initialized by decorator.
        """
        msg = f"{interaction.user.name} started a game.\n"
        self.client.logger.info(msg)

        await interaction.response.defer()
        round_end_time = int(time.time() + difficulty.value)

        article = await self.client.database_handler.get_random_article()
        embed = create_article_embed(article, self.game.players[0], self.game, round_end_time)

        self.game.start_game(article_timer=difficulty.value)
        self.game.start_article_timer()

        # The Sessions table in the database tracks users and scores
        session_records = await self.client.database_handler.start_new_sessions(self.game.player_ids)
        for player, session_record in zip(self.game.players, session_records, strict=False):
            self.game.add_session_id_for_player(player=player, session_id=session_record.id)

        await interaction.edit_original_response(
            embed=embed,
            view=GameView(
                og_interaction=self.og_interaction,
                article=article,
                game=self.game,
                client=self.client,
                round_end_time=round_end_time,
            ),
        )
