import discord, os, platform
from discord.ext import commands, tasks
from .tools.utils import color_message, get_json_file, update_json_file, read_text_file
from .constants import INTENTS, NEWS_STATIONS, OWNER_IDS
from random import choice
from .exceptions import InvalidTokenError

os.chdir("article_overload")


class ArticleOverloadBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="ao!", intents=INTENTS, owner_ids=OWNER_IDS)

    def initialize(self, token: str):
        if platform.system() == "Windows":
            os.system("cls")

        else:
            os.system("reset")

        print(
            color_message(
                message=read_text_file("./assets/ascii_bot.txt"), color="yellow"
            )
        )
        print(color_message(message="Bot has started", color="green"))

        try:
            self.run(token)

        except InvalidTokenError:
            print(color_message(message="Invalid Token", color="red"))

    async def load_extensions(self):
        startup_config = get_json_file("./bot_data/startup_config.json")

        for cog in os.listdir("./cogs"):
            if cog.endswith(".py"):
                try:
                    await self.load_extension(name=f"article_overload.cogs.{cog[:-3]}")

                    print(color_message(message=f"Loaded {cog[:-3]} cog", color="blue"))

                except Exception as e:
                    print(
                        color_message(
                            message=f"Failed to load {cog[:-3]} cog. Traceback: ",
                            color="red",
                        )
                        + str(e)
                    )

        update_json_file(startup_config, "./bot_data/startup_config.json")

    @commands.Cog.listener()
    async def on_ready(self):
        print(color_message(message=f"Logged in as {self.user}!", color="green"))

        await self.load_extensions()
        await self.tree.sync()

        self.update_presence.start()

    @commands.Cog.listener()
    async def on_close(self):
        print(color_message(message=f"Shutting down {self.user}...", color="green"))

    @tasks.loop(seconds=5)
    async def update_presence(self):
        await self.wait_until_ready()

        await self.change_presence(
            status=discord.Status.online,
            activity=discord.Activity(
                type=discord.ActivityType.playing, name=choice(NEWS_STATIONS)
            ),
        )
