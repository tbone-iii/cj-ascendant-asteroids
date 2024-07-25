from discord import Interaction, app_commands
from discord.ext import commands
from utils.game_classes import Game, Player

from article_overload.bot import ArticleOverloadBot
from article_overload.tools.desc import CommandDescriptions
from article_overload.tools.utils import create_warning_embed
from article_overload.views import ButtonView


class ArticleOverload(commands.Cog):
    """ArticleOverload cog class."""

    def __init__(self, client: ArticleOverloadBot) -> None:
        """Initialize method.

        Description: Initialize ArticleOverload cog as a subclass of commands.Cog
        :Return: None
        """
        self.client = client
        self.games: dict[int, Game] = {}

    @app_commands.command(
        name="article_overload",
        description=CommandDescriptions.GAME_START.value,
    )
    async def article_overload(self, interaction: Interaction) -> None:
        """Bot command.

        Description: Starts the game
        :Return: None
        """
        if interaction.user.id in self.games:
            return await interaction.response.send_message(
                embed=create_warning_embed(
                    title="Already In Game!",
                    description="You are already in a game!",
                ),
            )

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
        game.start_game()

        self.games.update({interaction.user.id: game})

        # Create an embed to display the player details
        embed = game.create_start_game_embed(player)
        return await interaction.response.send_message(embed=embed, view=ButtonView(interaction, embed))

    @app_commands.command(name="end_game", description=CommandDescriptions.GAME_END.value)
    async def end_game(self, interaction: Interaction) -> None:
        """Bot command.

        Description: Ends the game
        :Return: None
        """
        game = self.games.get(interaction.user.id, None)
        if game is None:
            return await interaction.response.send_message(
                embed=create_warning_embed(
                    title="Not In Game!",
                    description="You are not in a game!",
                ),
            )

        game.end_game()
        self.games.pop(interaction.user.id)

        return await interaction.response.send_message("Game ended!")


async def setup(client: ArticleOverloadBot) -> None:
    """Set up command.

    Description: Sets up the ArticleOverload Cog
    :Return: None
    """
    await client.add_cog(ArticleOverload(client))
