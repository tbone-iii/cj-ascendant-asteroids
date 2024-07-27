from discord import ButtonStyle, Interaction
from discord.ui import Button, View, button
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

    @button(label="Start", style=ButtonStyle.blurple)
    async def button_callback1(
        self,
        interaction: Interaction,
        _: Button,
    ) -> None:
        """Responds to button interaction.

        Description: Callback function for the button initialized by decorator.
        """
        await interaction.response.defer()

        article = await self.client.database_handler.get_random_article()

        self.game.start_game()

        self.game.start_article_timer()

        player = self.game.get_player(self.og_interaction.user.id)

        embed = create_article_embed(article, player, self.game)

        await interaction.edit_original_response(
            embed=embed,
            view=GameView(self.og_interaction, article, self.game, self.client),
        )
