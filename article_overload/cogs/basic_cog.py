from discord import Embed, Interaction, app_commands
from discord.ext import commands

from article_overload.bot import ArticleOverloadBot
from article_overload.mention_target import MentionTarget
from article_overload.tools.desc import CommandDescriptions
from article_overload.tools.utils import create_success_embed, create_warning_embed
from article_overload.views import ButtonView, ConfirmDeny, InputButton, PaginationView, SelectOptionsView
from article_overload.views.confirm_deny import ConfirmDenyOptions


class Sample(commands.Cog):
    """Sample cog class."""

    def __init__(self, client: ArticleOverloadBot) -> None:
        """Initialize method.

        Description Initialize commands.Cog subclass.
        :Return: None
        """
        self.client = client

    @app_commands.command(name="ping", description=CommandDescriptions.PING.value)
    async def ping(self, interaction: Interaction) -> None:
        """Bot command.

        Description: Returns pong
        :Return: None
        """
        await interaction.response.send_message("pong")

    @app_commands.command(name="create_embed", description=CommandDescriptions.CREATE_EMBED.value)
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
        description=CommandDescriptions.CREATE_BUTTON_EXAMPLE.value,
    )
    async def create_button(self, interaction: Interaction) -> None:
        """Bot command.

        Description: Creates a view from ButtonViews containing buttons
        :Return: None
        """
        await interaction.response.send_message(view=ButtonView())

    @app_commands.command(
        name="greet",
        description=CommandDescriptions.GREET.value,
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

    @app_commands.command(name="confirm_deny", description=CommandDescriptions.CONFIRM_DENY.value)
    async def confirm_deny(self, interaction: Interaction) -> None:
        """Bot command.

        Description: Shows a confirmation message with options to confirm or deny
        :Return: None
        """
        await interaction.response.defer()
        view = ConfirmDeny(org_user=interaction.user.id)
        await interaction.followup.send(
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

    @app_commands.command(name="user_input", description=CommandDescriptions.USER_INPUT.value)
    async def user_input(self, interaction: Interaction) -> None:
        """Bot command.

        Description: Collects input from the user and stores it to be processed
        :Return: None
        """
        await interaction.response.defer()

        view = InputButton(
            title="Ascendant Asteroid #1",
            message="Will Ascendant Asteroid win the Code Jam?",
            org_user=interaction.user.id,
        )
        embed = Embed(
            title="Important Question",
            description="Please press the button below to answer a short question",
        )
        await interaction.followup.send(embed=embed, view=view)
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

    @app_commands.command(name="select_stuff", description=CommandDescriptions.SELECT_STUFF.value)
    async def select_stuff(self, interaction: Interaction) -> None:
        """Bot command.

        Description: Enables user to select items for a menu and displays them
        :Return: None
        """
        await interaction.response.defer()

        view = SelectOptionsView(
            interaction.user.id,
            [str(i) + str(i) for i in range(100)],
            [str(i) for i in range(100)],
        )
        await interaction.followup.send(content="Select", view=view)
        await view.wait()

        await interaction.edit_original_response(content="You selected:\n" + "\n".join(view.clicked), view=None)

    @app_commands.command(name="pagination", description=CommandDescriptions.PAGINATION.value)
    async def pagination(self, interaction: Interaction) -> None:
        """Bot command.

        Description: Enables user to page through items in embeds
        :Return: None
        """
        await interaction.response.defer()

        view = PaginationView(
            interaction.user.id,
            [
                {
                    "embed": Embed(title=str(i) * 5, description=str(i) * 3),
                    "title": str(i),
                    "description": str(i) * 2,
                    "num": i + 1,
                }
                for i in range(100)
            ],
        )
        await interaction.followup.send(embed=Embed(title="Page through stuff"), view=view)
        await view.wait()


async def setup(client: ArticleOverloadBot) -> None:
    """Set up command.

    Description: Sets up the Sample Cog
    :Return: None
    """
    await client.add_cog(Sample(client))
