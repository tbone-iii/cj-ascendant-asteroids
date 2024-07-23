from discord import Embed, Interaction, app_commands
from discord.ext import commands

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


async def setup(client: ArticleOverloadBot) -> None:
    """Sets up command.

    Description: Sets up the Basic Cog
    :Return: None
    """
    await client.add_cog(Basic(client))
