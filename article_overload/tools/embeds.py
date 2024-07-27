from discord import Color, Embed
from discord.app_commands import MissingPermissions
from utils.constants import ARTICLE_TIMER
from utils.game_classes import Game, Player

from article_overload.constants import (
    COLOR_BAD,
    COLOR_GOOD,
    COLOR_NEUTRAL,
    CORRECT_ANSWER_POINTS,
    INCORRECT_ANSWER_POINTS,
)
from article_overload.db.objects import Article
from article_overload.exceptions import PlayerNotFoundError


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


def create_article_embed(article: Article, player: int | Player, game: Game) -> Embed:
    """Create a Discord embed containing the article summary and options a user can pick from.

    Parameters
    ----------
    article : Article
        The article to retrieve the summary from

    player : Integer | Player
        The player_id or player object for whom the embed is to be created.

    game : Game
        The game for which the article embed should be created for

    Returns
    -------
    discord.Embed
        A Discord embed object containing the player's details.

    """
    embed = Embed(
        title="Article Overload!",
        description=f"Please read the following article summary and use the \
            select menu below to choose which sentence is false:\n\n{article.marked_up_summary}",
    )
    embed.add_field(name="Time Left", value=f"Ending <t:{int(game.article_timer_start+ARTICLE_TIMER)}:R>")

    player_instance = game.get_player(player) if isinstance(player, int) else player
    if player_instance is None:
        raise PlayerNotFoundError

    embed.add_field(
        name="Answer Streak",
        value=str(player_instance.answer_streak),
    )
    return embed


def create_correct_answer_embed(player: Player) -> Embed:
    """Create a Discord embed for getting a correct answer.

    Description: Sends user an embed containing points gained and answer streak

    Parameters
    ----------
    player : Player
        The player object for whom the embed is to be created.

    Returns
    -------
    discord.Embed
        A Discord embed object containing the player's details

    """
    return Embed(
        title="Correct!",
        description=f"You have correctly deduced the false statement from the article! \
                    You gained {CORRECT_ANSWER_POINTS} points and your score is now {player.get_score()}. \
                        Press continue to move on",
        color=COLOR_GOOD,
    )


def create_incorrect_answer_embed(player: Player, article: Article) -> Embed:
    """Create a Discord embed for getting an incorrect answer.

    Description: Sends user an embed containing points lost and reset answer streak

    Parameters
    ----------
    player : Player
        The player object for whom the embed is to be created.

    article : Article
        The article containing the correct answer option

    Returns
    -------
    discord.Embed
        A Discord embed object containing the player's details

    """
    return Embed(
        title="Incorrect!",
        description=f"You did not select the false statement correctly! You lost {INCORRECT_ANSWER_POINTS} points \
            and your score is now {player.get_score()}! \
                    Press continue to move on\n\nCorrect Answer: {article.highlight_answer_in_summary}",
        color=COLOR_BAD,
    )


def create_time_up_embed(player: int | Player, game: Game) -> Embed:
    """Create a Discord embed saying game over.

    Description: Game over due to time and contains user statistics from the game.

    Parameters
    ----------
    player : Integer | Player
        The player_id or player object for whom the embed is to be created.

    game : Game
        The game for which the article embed should be created for

    Returns
    -------
    discord.Embed
        A Discord embed object containing the player's details.

    """
    player_instance = game.get_player(player) if isinstance(player, int) else player
    if player_instance is None:
        raise PlayerNotFoundError

    return Embed(
        title="Game Over!",
        description=(
            "You ran out of time! Here are your statistics from this game:\n"
            f"Score: {player_instance.get_score()}\n"
            f"Game Time: {game.get_game_duration()}\n"
            f"Correct: {player_instance.correct}\n"
            f"Incorrect: {player_instance.incorrect}\n"
        ),
    )


def create_too_many_incorrect_embed(player: Player, game: Game) -> Embed:
    """Create a Discord embed saying game over.

    Description: Game over due to too many
    incorrect answers and contains user statistics from the game.

    Parameters
    ----------
    player : Integer | Player
        The player_id or player object for whom the embed is to be created.

    game : Game
        The game for which the article embed should be created for

    Returns
    -------
    discord.Embed
        A Discord embed object containing the player's details.

    """
    return Embed(
        title="Game Over!",
        description=(
            "You got too many questions wrong! Here are your statistics from this game:\n"
            f"Score: {player.get_score()}\n"
            f"Game Time: {game.get_game_duration()}\n"
            f"Correct: {player.correct}\n"
            f"Incorrect: {player.incorrect}\n"
        ),
    )


def get_player_from_id_or_instance(player: int | Player, game: Game) -> Player | None:
    """Get the player instance from the player ID or the player instance.

    Parameters
    ----------
    player : Integer | Player
        The player_id or player object for whom the embed is to be created.

    game : Game
        The game for which the article embed should be created for

    Returns
    -------
    Player
        The player instance

    """
    return game.get_player(player) if isinstance(player, int) else player
