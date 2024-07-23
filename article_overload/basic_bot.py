import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from article_overload.mention_target import MentionTarget

from .button_views import ButtonView
from .exceptions import MissingTokenError
from utils.game_classes import Game, Player, Ability

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
        # Initialize the Discord Game
        self.game = Game()

        @self.event
        async def on_ready() -> None:
            """Bot event.

            :Return: None
            """
            print(f"logged on as {self.user}")

        @self.command()
        async def ping(context: commands.Context) -> None:
            """Bot command.

            :Return: None
            """
            await context.send("pong")

        @self.command()
        async def create_embed(context: commands.Context) -> None:
            """Bot command.

            Description: Creates a basic discord.Embed
            :Return: None
            """
            embed = discord.Embed(title="This is an embed")
            embed.add_field(name="Field", value="field value")
            await context.send(embed=embed)

        @self.command(
            name="create_button_example",
            description="Creates a view from ButtonViews containing buttons.",
        )
        async def create_button(context: commands.Context) -> None:
            """Bot command.

            Description: Creates a view from ButtonViews containing buttons
            :Return: None
            """
            await context.send(view=ButtonView())

        @self.command(
            name="greet",
            description="Greets the server with the option to mention `everyone`.",
        )
        async def greet(context: commands.Context, mention_target_string: str = "") -> None:
            """Bot command.

            Description: Greets the server with the option to mention @everyone
            :Return: None
            """
            try:
                mention_target = MentionTarget(mention_target_string)
            except ValueError:
                await context.send("Invalid mention target. Please try again.")
                return

            mention_value = " @everyone" if mention_target == MentionTarget.EVERYONE else ""
            await context.send(f"Greetings{mention_value}!")

        @self.command(name="start_game", description="Starts the game.")
        async def start_game(context: commands.Context) -> None:
            """Bot command.

            Description: Starts the game
            :Return: None
            """
            author = context.author
            player = Player(player_id=author.id,
                            name=author.name,
                            display_name=author.display_name,
                            avatar_url=author.avatar.url)
            self.game.add_player(player)
            self.game.start_game()

            # Create an embed to display the player details
            embed = discord.Embed(title="The Information Overload Game!", color=discord.Color.green())
            embed.add_field(name="Player ID", value=player.get_player_id(), inline=False)
            embed.add_field(name="Display Name", value=player.get_display_name(), inline=False)
            embed.add_field(name="Score", value=player.get_score(), inline=False)
            embed.set_thumbnail(url=player.get_avatar_url())

            await context.send(embed=embed)

        @self.command(name="end_game", description="Ends the game.")
        async def end_game(context: commands.Context) -> None:
            """Bot command.

            Description: Ends the game
            :Return: None
            """
            self.game.end_game()
            await context.send("Game ended!")

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
