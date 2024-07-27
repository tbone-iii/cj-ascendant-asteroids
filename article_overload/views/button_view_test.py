import time

from discord import ButtonStyle, Embed, Interaction
from discord.ui import Button, View, button
from utils.constants import DifficultyTimer
from utils.game_classes import Game

from article_overload.bot import ArticleOverloadBot

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

        article = await self.client.database_handler.get_random_article()
        embed = Embed(
            title="Article Overload!",
            description="Please read the following article summary and "
            "use the select menu below to choose which sentence is false:",
        )
        embed.add_field(name="", value=f"{article.marked_up_summary}")
        embed.add_field(
            name="Round ends:",
            value=f"<t:{int(time.time() + difficulty.value)}:R>",
            inline=True,
        )

        self.game.start_game(article_timer=difficulty.value)
        self.game.start_article_timer()

        await interaction.edit_original_response(
            embed=embed,
            view=GameView(
                og_interaction=self.og_interaction,
                article=article,
                game=self.game,
                client=self.client,
            ),
        )
