from discord import Embed, Interaction, app_commands
from discord.ext import commands

from article_overload.bot import ArticleOverloadBot
from article_overload.mention_target import MentionTarget
from article_overload.tools.desc import COMMAND_DESC
from article_overload.tools.utils import create_success_embed, create_warning_embed
from article_overload.views import ButtonView, ConfirmDeny, InputButton
from article_overload.views.confirm_deny import ConfirmDenyOptions


class Sample(commands.Cog):
    """Sample cog class."""

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

    @app_commands.command(name="confirm_deny", description=COMMAND_DESC["confirm_deny"])
    async def confirm_deny(self, interaction: Interaction) -> None:
        """Bot command.

        Description: Shows a confirmation message with options to confirm or deny
        :Return: None
        """
        # TODO: Figure out why user gets interaction failed even
        # if there is no error and everything passes successfully
        view = ConfirmDeny(org_user=interaction.user.id)
        await interaction.response.send_message(
            embed=create_warning_embed(
                title="Are you sure?",
                description="Do you want to confirm?",
            ),
            view=view,
        )
        await view.wait()

        if view.value == ConfirmDenyOptions.YES:
            await interaction.edit_original_response(
                embed=create_success_embed(
                    title="Success!",
                    description="You have confirmed that you want to donate your life savings to the \
                        Ascendant Asteroid group!",
                ),
                view=None,
            )

        elif view.value == ConfirmDenyOptions.NO:
            await interaction.edit_original_response(
                embed=create_success_embed(
                    title="Operation Canceled",
                    description="You have declined the offer to donate to the Ascendant Asteroid group",
                ),
                view=None,
            )

        elif view.value == ConfirmDenyOptions.EXPIRED:
            await interaction.edit_original_response(
                embed=create_warning_embed(
                    title="Too Late!",
                    description="Your chance to donate your life savings to the \
                        Ascendant Asteroid group has expired! Better luck next time!",
                ),
                view=None,
            )

    @app_commands.command(name="user_input", description=COMMAND_DESC["user_input"])
    async def user_input(self, interaction: Interaction) -> None:
        """Bot command.

        Description: Collects input from the user and stores it to be processed
        :Return: None
        """
        # TODO: Figure out why user gets interaction failed even
        # if there is no error and everything passes successfully
        view = InputButton(
            title="Ascendant Asteroid #1",
            message="Will Ascendant Asteroid win the Code Jam?",
            org_user=interaction.user.id,
        )
        embed = Embed(
            title="Important Question",
            description="Please press the button below to answer a short question",
        )
        await interaction.response.send_message(embed=embed, view=view)
        await view.wait()

        if view.response is None:
            await interaction.edit_original_response(
                embed=create_warning_embed(
                    title="Expired!",
                    description="Your chance to praise the Ascendant Asteroids has expired. Please try again later",
                ),
                view=None,
            )

        else:
            await interaction.edit_original_response(
                embed=create_success_embed(
                    title="Success!",
                    description=f"Your thoughtful response has been recorded! \
                        You submitted the following text:\n**{view.response}**",
                ),
                view=None,
            )


async def setup(client: ArticleOverloadBot) -> None:
    """Set up command.

    Description: Sets up the Sample Cog
    :Return: None
    """
    await client.add_cog(Sample(client))
