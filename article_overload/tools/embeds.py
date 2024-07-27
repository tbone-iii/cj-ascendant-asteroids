from discord import Embed, Color
from discord.app_commands import MissingPermissions

from article_overload.constants import COLOR_BAD, COLOR_GOOD, COLOR_NEUTRAL
from article_overload.db.objects import Article
from utils.constants import ARTICLE_TIMER
from utils.game_classes import Game, Player


def create_success_embed(title: str = "\u200b", description: str = "\u200b") -> Embed:
    """Embed creator.

    Description: Creates a success embed.
    :Return: Embed
    """
    embed = Embed(title=title, description=description, color=COLOR_GOOD)
    embed.set_thumbnail(
        url="https://media3.giphy.com/media/CaS9NNso512WJ4po0t/giphy.gif?cid=ecf05e47mgm8u6fljfxl5d5g0s01tp94qgn9exfwqvlpi3id&rid=giphy.gif&ct=s",
    )
    return embed


def create_warning_embed(title: str = "\u200b", description: str = "\u200b") -> Embed:
    """Embed creator.

    Description: Creates a warning embed.
    :Return: Embed
    """
    embed = Embed(title=title, description=description, color=COLOR_NEUTRAL)
    embed.set_thumbnail(
        url="https://c.tenor.com/26pNa498OS0AAAAi/warning-joypixels.gif",
    )
    return embed


def create_error_embed(title: str = "\u200b", description: str = "\u200b") -> Embed:
    """Embed creator.

    Description: Creates an error embed.
    :Return: Embed
    """
    embed = Embed(title=title, description=description, color=COLOR_BAD)
    embed.set_thumbnail(
        url="https://i.gifer.com/origin/bf/bf2d25254a2808835e20c9d698d75f28_w200.gif",
    )
    return embed

def create_missing_permissions_embed(
    error: MissingPermissions,
) -> Embed:  # TODO: Review what actual error type is and where it's sourced from
    """Missing permissions embed.

    Description: Creates an error embed for missing permissions.
    :Return: Embed
    """
    missing_permissions = ",".join(error.missing_permissions)
    return create_error_embed(
        title="Missing Permissions!",
        description=f"You cannot run this command as you are missing the following permissions: {missing_permissions}",
    )


def create_action_canceled_embed() -> Embed:
    """Cancel action embed.

    Description: Creates a warning embed for canceling an action.
    :Return: Embed
    """
    return create_warning_embed(title="Action canceled")


def create_error_occurred_embed() -> Embed:
    """Error embed.

    Description: Creates an error embed for an unknown error occurring.
    :Return: Embed
    """
    return create_error_embed(
        title="Error!",
        description="An error has occurred while running your command!",
    )


def create_start_game_embed(player: Player) -> Embed:
    """Create a Discord embed for the start of the game.

    Parameters
    ----------
    player : Player
        The player for whom the embed is to be created.

    Returns
    -------
    discord.Embed
        A Discord embed object containing the player's details.

    """
    embed = Embed(
        title="Welcome to Article Overload",
        color=Color.green(),
    )
    embed.add_field(name="Player ID", value=player.get_player_id(), inline=False)
    embed.add_field(
        name="Display Name",
        value=player.get_display_name(),
        inline=False,
    )
    embed.add_field(name="Score", value=player.get_score(), inline=False)
    embed.set_thumbnail(url=player.get_avatar_url())
    return embed


def create_article_embed(article: Article, player_id: int, game: Game) -> Embed:
    embed = Embed(title="Article Overload!", description=f"Please read the following article summary and use the select menu below to choose which sentence is false:\n\n{article.marked_up_summary}")
    embed.add_field(name="Time Left", value=f"Ending <t:{int(game.article_timer_start+ARTICLE_TIMER)}:R>")
    embed.add_field(name="Answer Streak", value=str(game.get_player(player_id).answer_streak))
    return embed


def create_time_up_embed(player: Player, game: Game) -> Embed:
    embed = Embed(title="Game Over!", description=f"You ran out of time! Here are your statistics from this game:\nScore: {player.get_score()}\nGame Time: {game.get_game_duration()}\nCorrect: {player.correct}\nIncorrect: {player.incorrect}")

    return embed

def create_too_many_incorrect_embed(player: Player, game: Game) -> Embed:
    embed = Embed(title="Game Over!", description=f"You got too many questions wrong! Here are your statistics from this game:\nScore: {player.get_score()}\nGame Time: {game.get_game_duration()}\nCorrect: {player.correct}\nIncorrect: {player.incorrect}")

    return embed