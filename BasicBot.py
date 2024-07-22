import os

import discord
from button_views import ButtonView
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()  # Loads .env contents


class BasicBot(commands.Bot):
    """Basic bot class."""

    def __init__(
        self,
        *args: any,
        command_prefix: str = ".",
        intents: discord.Intents = discord.Intents.default,
    ) -> None:
        """Initialize commands.Bot subclass.

        :return: None
        """
        super().__init__(*args, command_prefix=command_prefix, intents=intents)

        @self.event
        async def on_ready() -> None:
            """Bot event.

            :return: None
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

        @self.command()
        async def create_button(context: commands.Context) -> None:
            """Bot command.

            Description: Creates a view from ButtonViews containing buttons
            :Return: None
            """
            await context.send(view=ButtonView())

        @self.command()
        async def greet(context: commands.Context, mention: str = "") -> None:
            """Bot command.

            Description: Greets the server with the option to mention @everyone
            (Ruff seems to strongly dislike mention being typed as a bool, so str it is)
            :Return: None
            """
            await context.send(f'Greetings{" @everyone" if mention.lower()=="mention" else ""}!')


# Bot Parameters -----------------------------

intents = discord.Intents.default()
intents.message_content = True

# Run that mf --------------------------------

if __name__ == "__main__":
    bot = BasicBot(intents=intents)
    bot.run(os.getenv("TOKEN"))
