import os
import platform
import secrets
import subprocess

import discord
from discord.ext import commands, tasks

from .constants import IGNORE_FILES, INTENTS, NEWS_STATIONS, OWNER_IDS
from .exceptions import InvalidTokenError, NoTokenProvidedError
from .tools.utils import color_message, get_json_file, read_text_file, update_json_file

os.chdir("article_overload")  # TODO: Change this to pathlib usage


class ArticleOverloadBot(commands.Bot):
    """ArticleOverloadBot class."""

    def __init__(self) -> None:
        """Initialize method.

        Description: Initialize commands.Bot subclass
        :Return: None
        """
        super().__init__(command_prefix="ao!", intents=INTENTS, owner_ids=OWNER_IDS)
        self.unloaded_cogs = []

    def start_bot(self, token: str | None) -> None:
        """Start the bot.

        Description: Runs the bot with a token
        :Return: None
        """
        if token is None:
            raise NoTokenProvidedError

        clear_console()

        print(
            color_message(
                message=read_text_file("./assets/ascii_bot.txt"),
                color="yellow",
            ),
        )
        print(color_message(message="Bot has started", color="green"))

        try:
            self.run(token)
        except InvalidTokenError:
            print(color_message(message="Invalid Token", color="red"))

    async def load_extensions(self) -> None:
        """Load extensions.

        Description: Loads all bot extensions
        :Return: None
        """
        startup_config = get_json_file("./bot_data/startup_config.json")

        for cog in [file for file in os.listdir("./cogs") if file.endswith(".py") and file not in IGNORE_FILES]:
            if cog[:-3] not in startup_config:
                startup_config[cog[:-3]] = {"enabled": False}

            if not startup_config[cog[:-3]]["enabled"]:
                print(
                    color_message(
                        message=f"Skipping {cog[:-3]} as it is not enabled",
                        color="yellow",
                    ),
                )
                self.unloaded_cogs.append(cog[:-3])
                continue

            try:
                await self.load_extension(name=f"article_overload.cogs.{cog[:-3]}")
                print(color_message(message=f"Loaded {cog[:-3]} cog", color="blue"))
            except discord.DiscordException as e:
                print(
                    color_message(
                        message=f"Failed to load {cog[:-3]} cog. Traceback: ",
                        color="red",
                    )
                    + str(e),
                )

        update_json_file(startup_config, "./bot_data/startup_config.json")

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """On ready event.

        Description: Bot listener that checks if bot is ready
        :Return: None
        """
        print(color_message(message=f"Logged in as {self.user}!", color="green"))

        await self.load_extensions()
        await self.sync_commands()

        self.update_presence.start()

    @commands.Cog.listener()
    async def on_close(self) -> None:
        """On close event.

        Description: Bot listener that checks if the bot is shutting down
        :Return: None
        """
        print(
            color_message(
                message=f"Shutting down {self.user}article_overload..",
                color="green",
            ),
        )

    @tasks.loop(seconds=5)
    async def update_presence(self) -> None:
        """Presence update task.

        Description: Task that updates bot's rich presence
        :Return: None
        """
        await self.wait_until_ready()
        await self.change_presence(
            status=discord.Status.online,
            activity=discord.Activity(
                type=discord.ActivityType.playing,
                name=secrets.choice(NEWS_STATIONS),
            ),
        )

    async def sync_commands(self) -> None:
        """Sync the slash commands list.

        Description: Sync the slash commands list with the bot for each guild (server).
        :Return: None
        """
        for guild in self.guilds:
            self.tree.clear_commands(guild=guild)
            await self.tree.sync(guild=guild)


def clear_console() -> None:
    """Clear the console screen."""
    if platform.system() == "Windows":
        subprocess.run(["cmd.exe", "/c", "cls"], check=True)  # noqa: S603, S607, ruff is overly strict here
    else:
        subprocess.run(["clear"], check=True)  # noqa: S603, S607, ruff is overly strict here
