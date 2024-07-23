from discord import Interaction
from discord.ext import commands
from discord.app_commands import MissingPermissions
from ..bot import ArticleOverloadBot
from ..tools.embeds import missing_permissions, error_occurred


class Error(commands.Cog):
    def __init__(self, client: ArticleOverloadBot):
        self.client = client

    @commands.Cog.listener()
    async def on_application_command_error(
        self, interaction: Interaction, error: Exception
    ):
        if isinstance(error, MissingPermissions):
            await interaction.response.send_message(
                embed=missing_permissions(error=error),
            )

        else:
            await interaction.response.send_message(embed=error_occurred())

        raise error


async def setup(client: ArticleOverloadBot):
    await client.add_cog(Error(client))
