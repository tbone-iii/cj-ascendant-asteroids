from discord import Embed, Interaction, app_commands
from discord.ext import commands
from utils.game_classes import Game, Player

from article_overload.bot import ArticleOverloadBot
from article_overload.mention_target import MentionTarget
from article_overload.tools.desc import COMMAND_DESC
from article_overload.views import ButtonView


class Basic(commands.Cog):
    """Basic cog class."""

    def __init__(self, client: ArticleOverloadBot) -> None:
        """Initialize method.

        Description Initialize commands.Cog subclass.
        :Return: None
        """
        self.client = client
        self.game = Game()

    @app_commands.command(name="ping", description=COMMAND_DESC["ping"])
    async def ping(self, interaction: Interaction) -> None:
        """Bot command.

        Description: Returns pong
        :Return: None
        """
        await interaction.response.send_message("pong")

    @app_commands.command(name="create_embed", description=COMMAND_DESC["create_embed"])
    async def create_embed(self, interaction: Interaction) -> None:
        """Bot command.

        Description: Creates a basic discord.Embed
        :Return: None
        """
        embed = Embed(title="This is an embed")
        embed.add_field(name="Field", value="field value")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="create_button_example",
        description=COMMAND_DESC["create_button_example"],
    )
    async def create_button(self, interaction: Interaction) -> None:
        """Bot command.

        Description: Creates a view from ButtonViews containing buttons
        :Return: None
        """
        await interaction.response.send_message(view=ButtonView())

    @app_commands.command(
        name="greet",
        description=COMMAND_DESC["greet"],
    )
    async def greet(
        self,
        interaction: Interaction,
        mention_target_string: str = "",
    ) -> None:
        """Bot command.

        Description: Greets the server with the option to mention @everyone
        :Return: None
        """
        try:
            mention_target = MentionTarget(mention_target_string)
        except ValueError:
            await interaction.response.send_message(
                "Invalid mention target. Please try again.",
            )
            return

        mention_value = " @everyone" if mention_target == MentionTarget.EVERYONE else ""
        await interaction.response.send_message(f"Greetings{mention_value}!")

    @app_commands.command(
        name="article_overload",
        description=COMMAND_DESC["game_start"],
    )
    async def article_overload(self, interaction: Interaction) -> None:
        """Bot command.

        Description: Starts the game
        :Return: None
        """
        author = interaction.user
        url = author.avatar.url if author.avatar else ""
        player = Player(
            player_id=author.id,
            name=author.name,
            display_name=author.display_name,
            avatar_url=url,
        )
        self.game.add_player(player)
        self.game.start_game()

        # Create an embed to display the player details
        embed = self.game.create_start_game_embed(player)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="end_game", description=COMMAND_DESC["game_end"])
    async def end_game(self, interaction: Interaction) -> None:
        """Bot command.

        Description: Ends the game
        :Return: None
        """
        self.game.end_game()
        await interaction.response.send_message("Game ended!")


async def setup(client: ArticleOverloadBot) -> None:
    """Set up command.

    Description: Sets up the Basic Cog
    :Return: None
    """
    await client.add_cog(Basic(client))
