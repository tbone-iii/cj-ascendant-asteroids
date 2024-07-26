import logging

from discord import Interaction, app_commands
from discord.app_commands import AppCommandError
from discord.ext import commands

from article_overload.bot import ArticleOverloadBot


# May be better as its own module instead of a cog, that way we can
# refer to it in other parts of the bot and have it log the info we
# want to log.
class Logger(commands.Cog):
    """Logger."""

    def __init__(self, bot: ArticleOverloadBot, log_level: int = logging.INFO) -> None:
        self.bot = bot
        # -- Logging setup -----------------
        self.logger = logging.getLogger("discord")
        self.logger.setLevel(log_level)
        logging.getLogger("discord.http").setLevel(logging.INFO)
        logging.getLogger("discord.client").setLevel(logging.INFO)
        logging.getLogger("discord.gateway").setLevel(logging.INFO)
        logging.getLogger("discord.webhook").setLevel(logging.INFO)
        handler = logging.handlers.RotatingFileHandler(
            filename="discord.log",
            encoding="utf-8",
            maxBytes=32 * 1024 * 1024,  # 32 MiB
            backupCount=5,  # Rotate through 5 files
        )
        dt_fmt = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter("[{asctime}] [{levelname:<8}] {name}: {message}", dt_fmt, style="{")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        # ATM, this lets us log info from other parts of the bot, but there
        # wont be any type hinting or lsp autocompletes and whatnot
        self.bot.logger = self.logger

    @commands.Cog.listener()
    async def on_app_command_completion(self, interaction: Interaction, command: app_commands.Command) -> None:
        """Log command info upon completion of an app command.

        Args:
        ----
            interaction: The discord.Interaction responsible for the command
            command: The app_commands.Command that was completed

        Returns:
        -------
            None

        """
        msg = f"{interaction.user.name} called {command.name}\n"
        self.logger.info(msg)

    @commands.Cog.listener(name="cog_app_command_error")
    async def cmd_error(self, _: Interaction, error: AppCommandError) -> None:
        """Log error info when an AppCommandError is raised from an app command.

        Args:
        ----
            interaction: discord.Interaction responsible for the command
            error: The AppCommandError raised

        Returns:
        -------
            None

        """
        msg = f"Error occured attempting to call app command.\nError:\n\t{error!s}"
        self.logger.info(msg)


async def setup(bot: ArticleOverloadBot) -> None:
    """Cog setup."""
    await bot.add_cog(Logger(bot, logging.DEBUG))
