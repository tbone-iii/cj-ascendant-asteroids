from discord import Interaction, app_commands
from discord.ext import commands
from utils.constants import ARTICLE_TIMER
from utils.game_classes import AbilityType, Game, Player

from article_overload.bot import ArticleOverloadBot
from article_overload.tools.desc import CommandDescriptions
from article_overload.tools.utils import create_warning_embed
from article_overload.views.button_view_test import StartButtonView


class ArticleOverload(commands.Cog):
    """ArticleOverload cog class."""

    def __init__(self, client: ArticleOverloadBot) -> None:
        """Initialize method.

        Description: Initialize ArticleOverload cog as a subclass of commands.Cog
        :Return: None
        """
        self.client = client
        self.games: dict[int, Game] = {}

    @app_commands.command(
        name="article_overload",
        description=CommandDescriptions.GAME_START.value,
    )
    async def article_overload(self, interaction: Interaction) -> None:
        """Bot command.

        Description: Starts the game
        :Return: None
        """
        if interaction.user.id in self.games:
            return await interaction.response.send_message(
                embed=create_warning_embed(
                    title="Already In Game!",
                    description="You are already in a game!",
                ),
            )

        game = Game()
        author = interaction.user
        url = author.avatar.url if author.avatar else ""
        player = Player(
            player_id=author.id,
            name=author.name,
            display_name=author.display_name,
            avatar_url=url,
        )
        game.add_player(player)
        game.start_game()

        self.games.update({interaction.user.id: game})

        # Create an embed to display the player details
        embed = game.create_start_game_embed(player)
        return await interaction.response.send_message(embed=embed, view=StartButtonView(interaction, embed))

    @app_commands.command(name="end_game", description=CommandDescriptions.GAME_END.value)
    async def end_game(self, interaction: Interaction) -> None:
        """Bot command.

        Description: Ends the game
        :Return: None
        """
        game = self.games.get(interaction.user.id, None)
        if game is None:
            return await interaction.response.send_message(
                embed=create_warning_embed(
                    title="Not In Game!",
                    description="You are not in a game!",
                ),
            )

        game.end_game()
        duration = game.get_game_duration()
        self.games.pop(interaction.user.id)

        return await interaction.response.send_message(f"Game ended! Duration: {duration}")

    # ===================================================================
    # Below commands are meant to demo the Game mechanics. In production,
    # this should be bound by the Discord UI
    # ===================================================================
    @app_commands.command(name="show_game_time", description="Shows the current game duration.")
    async def show_game_time(self, interaction: Interaction) -> None:
        """Bot command.

        Description: Shows the current game duration.
        :Return: None
        """
        game = self.games.get(interaction.user.id)
        if game is None:
            return await interaction.response.send_message("Game not found!", ephemeral=True)
        duration = game.get_game_duration()
        return await interaction.response.send_message(f"Current game duration: {duration}")

    @app_commands.command(name="show_article_timer", description="Shows the current article timer.")
    async def show_article_timer(self, interaction: Interaction) -> None:
        """Bot command.

        Description: Shows the current article timer.
        :Return: None
        """
        game = self.games.get(interaction.user.id)
        if game is None:
            return await interaction.response.send_message("Game not found!", ephemeral=True)
        timer = game.get_article_timer()
        return await interaction.response.send_message(f"Remaining time: {timer:.2f} seconds")

    @app_commands.command(name="start_new_article_challenge", description="Starts an article countdown.")
    async def start_new_article_challenge(self, interaction: Interaction) -> None:
        """Bot command.

        Description: Starts a new article challenge with a 15-second timer.
        :Return: None
        """
        game = self.games.get(interaction.user.id)
        if game is None:
            return await interaction.response.send_message("Game not found!", ephemeral=True)
        game.reset_article_timer()
        game.start_article_timer()
        return await interaction.response.send_message(f"New article: You have {ARTICLE_TIMER} seconds to answer.")

    @app_commands.command(name="increment_score", description="Increments the player's score by a given value.")
    async def increment_score(self, interaction: Interaction, points: int) -> None:
        """Bot command.

        Description: Increments the player's score by a given value.
        :Return: None
        """
        game = self.games.get(interaction.user.id)
        if game is None:
            return await interaction.response.send_message("Game not found!", ephemeral=True)
        player = game.get_player(interaction.user.id)
        if player is None:
            return await interaction.response.send_message("Player not found!", ephemeral=True)
        player.update_score(points)
        return await interaction.response.send_message(f"Score incremented! New score: {player.get_score()}")

    @app_commands.command(name="increase_abilities_meter", description="Increases player's ability meter at value")
    async def increase_abilities_meter(self, interaction: Interaction, value: int) -> None:
        """Bot command.

        Description: Increases the player's abilities meter by a given value.
        :Return: None
        """
        game = self.games.get(interaction.user.id)
        if game is None:
            return await interaction.response.send_message("Game not found!", ephemeral=True)
        player = game.get_player(interaction.user.id)
        if player is None:
            return await interaction.response.send_message("Player not found!", ephemeral=True)
        new_ability = player.update_abilities_meter(value)
        meter_percentage = player.get_abilities_meter_percentage()
        if new_ability:
            return await interaction.response.send_message(
                f"Fully Powered up! Got {new_ability.value} ability! Abilities meter now reset to {meter_percentage}%",
            )
        return await interaction.response.send_message(f"Abilities meter increased! Now at {meter_percentage}%")

    @app_commands.command(name="list_abilities", description="List all possible abilities.")
    async def list_abilities(self, interaction: Interaction) -> None:
        """Bot command to list all possible abilities."""
        abilities = [ability.value for ability in AbilityType]
        abilities_list = "\n".join(abilities)
        await interaction.response.send_message(f"Possible abilities:\n{abilities_list}")

    @app_commands.command(name="show_player_abilities", description="Shows the player's current abilities.")
    async def show_player_abilities(self, interaction: Interaction) -> None:
        """Bot command.

        Description: Shows the player's current abilities.
        :Return: None
        """
        game = self.games.get(interaction.user.id)
        if game is None:
            return await interaction.response.send_message("Game not found!", ephemeral=True)
        player = game.get_player(interaction.user.id)
        if player is None:
            return await interaction.response.send_message("Player not found!", ephemeral=True)
        abilities = player.get_abilities()
        abilities_list = ", ".join([ability.name for ability in abilities])
        return await interaction.response.send_message(f"Current abilities: {abilities_list}")

    @app_commands.command(name="add_ability", description="Add an ability to the player.")
    async def add_ability(self, interaction: Interaction, ability_name: str) -> None:
        """Bot command to add an ability to the player."""
        game = self.games.get(interaction.user.id)
        if game is None:
            return await interaction.response.send_message("Game not found!", ephemeral=True)

        player = game.get_player(interaction.user.id)
        if player is None:
            return await interaction.response.send_message("Player not found!", ephemeral=True)

        try:
            ability = AbilityType[ability_name.upper()]
            player.add_ability(ability)
            await interaction.response.send_message(f"Added {ability.value} ability to the player!")
        except KeyError:
            await interaction.response.send_message("Invalid ability name!", ephemeral=True)

    @app_commands.command(name="use_ability", description="Uses a player's ability.")
    async def use_ability(self, interaction: Interaction, ability: AbilityType) -> None:
        """Bot command to use a player's ability."""
        game = self.games.get(interaction.user.id)
        if not game:
            return await interaction.response.send_message("Game not found!", ephemeral=True)
        player = game.get_player(interaction.user.id)
        if not player:
            return await interaction.response.send_message("Player not found!", ephemeral=True)
        result = player.use_ability(ability, game)
        return await interaction.response.send_message(result)

    # ===================================================================
    # End of commands are meant to demo the Game mechanics
    # ===================================================================

async def setup(client: ArticleOverloadBot) -> None:
    """Set up command.

    Description: Sets up the ArticleOverload Cog
    :Return: None
    """
    await client.add_cog(ArticleOverload(client))
