import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
from utils.game_classes import Game, Player

from article_overload.mention_target import MentionTarget

from .button_views import ButtonView
from .exceptions import MissingTokenError

load_dotenv()  # Loads .env contents

# Configure base bot intents with message content enabled
intents = discord.Intents.default()
intents.message_content = True


class BasicBot(commands.Bot):
    """Basic bot class."""

    def __init__(
        self,
        intents: discord.Intents | None,
        command_prefix: str = "/",
    ) -> None:
        """Initialize commands.Bot subclass.

        :Return: None
        """
        if intents is None:
            intents = discord.Intents.default()

        super().__init__(command_prefix=command_prefix, intents=intents)
        self.game = Game()  # Start the Discord Game

        @self.tree.command(name="ping")
        async def ping(interaction: discord.Interaction) -> None:
            """Bot command.

            :Return: None
            """
            await interaction.response.send_message("pong")

        @self.tree.command(name="create_embed")
        async def create_embed(interaction: discord.Interaction) -> None:
            """Bot command.

            Description: Creates a basic discord.Embed
            :Return: None
            """
            embed = discord.Embed(title="This is an embed")
            embed.add_field(name="Field", value="field value")
            await interaction.response.send_message(embed=embed)

        @self.tree.command(
            name="create_button_example",
            description="Creates a view from ButtonViews containing buttons.",
        )
        async def create_button(interaction: discord.Interaction) -> None:
            """Bot command.

            Description: Creates a view from ButtonViews containing buttons
            :Return: None
            """
            await interaction.response.send_message(view=ButtonView())

        @self.tree.command(
            name="greet",
            description="Greets the server with the option to mention `everyone`.",
        )
        async def greet(interaction: discord.Interaction, mention_target_string: str = "") -> None:
            """Bot command.

            Description: Greets the server with the option to mention @everyone
            :Return: None
            """
            try:
                mention_target = MentionTarget(mention_target_string)
            except ValueError:
                await interaction.response.send_message("Invalid mention target. Please try again.")
                return

            mention_value = " @everyone" if mention_target == MentionTarget.EVERYONE else ""
            await interaction.response.send_message(f"Greetings{mention_value}!")

        @self.command(name="article_overload", description="Starts the game.")
        async def article_overload(context: commands.Context) -> None:
            """Bot command.

            Description: Starts the game
            :Return: None
            """
            author = context.author
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
            await context.send(embed=embed)

        @self.command(name="end_game", description="Ends the game.")
        async def end_game(context: commands.Context) -> None:
            """Bot command.

            Description: Ends the game
            :Return: None
            """
            self.game.end_game()
            await context.send("Game ended!")

    async def on_ready(self) -> None:
        """Bot event.

        :Return: None
        """
        for guild in self.guilds:
            self.tree.copy_global_to(guild=guild)
            print(f"Commands synced: {len(await self.tree.sync(guild=guild))}")
        print(f"logged on as {self.user}")


def main() -> None:
    """Configure and run the bot."""
    bot = BasicBot(intents=intents)
    token = os.getenv("TOKEN")

    if token is None:
        message = "Token is missing from environment variables."
        raise MissingTokenError(message)

    bot.run(token)


if __name__ == "__main__":
    main()
