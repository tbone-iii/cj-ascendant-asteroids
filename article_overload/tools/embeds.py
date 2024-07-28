import time
from secrets import choice

from discord import Color, Embed
from discord.app_commands import MissingPermissions

from article_overload.constants import (
    COLOR_BAD,
    COLOR_GOOD,
    COLOR_NEUTRAL,
    CORRECT_ANSWER_POINTS,
    INCORRECT_ANSWER_POINTS,
    ImageURLs,
)
from article_overload.db.items.article_handler import ArticleHandler
from article_overload.exceptions import PlayerNotFoundError
from article_overload.game_classes import Game, Player


def create_success_embed(title: str = "\u200b", description: str = "\u200b") -> Embed:
    """Embed creator.

    Description: Creates a success embed.
    :Return: Embed
    """
    embed = Embed(title=title, description=description, color=COLOR_GOOD)
    embed.set_thumbnail(
        url=ImageURLs.SUCCESS,
    )
    return embed


def create_warning_embed(title: str = "\u200b", description: str = "\u200b") -> Embed:
    """Embed creator.

    Description: Creates a warning embed.
    :Return: Embed
    """
    embed = Embed(title=title, description=description, color=COLOR_NEUTRAL)
    embed.set_thumbnail(
        url=choice(
            (
                ImageURLs.WARNING,
                ImageURLs.NOT_ALLOWED_SIGN,
            )
        ),
    )
    return embed


def create_error_embed(title: str = "\u200b", description: str = "\u200b") -> Embed:
    """Embed creator.

    Description: Creates an error embed.
    :Return: Embed
    """
    embed = Embed(title=title, description=description, color=COLOR_BAD)
    embed.set_thumbnail(
        url=choice(
            (
                ImageURLs.ERROR,
                ImageURLs.NO_FINGER,
            )
        )
    )
    return embed


def create_missing_permissions_embed(error: MissingPermissions) -> Embed:
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
    rules = (
        "\n**Game Rules**\n"
        "=========================================================\n"
        "1. **Objective**: Identify false statement in the provided article summaries using the dropdown options.\n\n"
        "2. **Game Duration**: The game continues until you end it or answer incorrectly too many times.\n\n"
        "3. **Scoring**: Points are awarded for each correct answer and deducted for each incorrect one.\n\n"
        "4. **Abilities**: Earn abilities that can help you in the game: add time, reduce options...\n\n"
        "5. **Timer**: Each article has a timer where length is based on your difficulty choice.\n\n"
    )

    embed = Embed(
        title="Welcome to Article Overload",
        description=(
            f"**Player Details**\n"
            f"**Player ID**: {player.get_player_id()}\n"
            f"**Display Name**: {player.get_display_name()}\n"
            f"**Score**: {player.get_score()}\n"
            f"{rules}"
        ),
        color=Color.green(),
    )
    embed.set_thumbnail(url=player.get_avatar_url())
    return embed


def create_article_embed(article_handler: ArticleHandler, player: int | Player, game: Game) -> Embed:
    """Create a Discord embed containing the article summary and options a user can pick from.

    Parameters
    ----------
    article_handler : ArticleHandler
        The article handler object containing the article to be displayed.

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
        description="Please read the following article summary and "
        "use the select menu below to choose which sentence is false:",
    )
    embed.add_field(name=article_handler.title, value=article_handler.marked_up_summary, inline=False)
    embed.add_field(
        name="Round ends:",
        value=f"<t:{int(time.time() + game.article_timer)}:R>",
        inline=False,
    )
    embed.set_footer(text=f"Author: {article_handler.author}")

    player_instance = game.get_player(player) if isinstance(player, int) else player
    if player_instance is None:
        raise PlayerNotFoundError

    embed.add_field(name="Answer Streak", value=str(player_instance.answer_streak), inline=False)
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


def create_incorrect_answer_embed(player: Player, highlighted_summary: str) -> Embed:
    """Create a Discord embed for getting an incorrect answer.

    Description: Sends user an embed containing points lost and reset answer streak

    Parameters
    ----------
    player : Player
        The player object for whom the embed is to be created.

    highlighted_summary : str
        The summary of the article with the false statement
        highlighted and true statements with strikethrough.

    Returns
    -------
    discord.Embed
        A Discord embed object containing the player's details

    """
    return Embed(
        title="Incorrect!",
        description=f"You did not select the false statement correctly! You lost {INCORRECT_ANSWER_POINTS} points \
            and your score is now {player.get_score()}! \
                    Press continue to move on\n\nCorrect Answer: {highlighted_summary}",
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
    padding_size = 15
    return Embed(
        title="Game Over!",
        description=(
            "You got too many questions wrong! Here are your statistics from this game:\n"
            f"`{'Score: ': <{padding_size}}{player.get_score(): <8}`\n"
            f"`{'Correct: ': <{padding_size}}{player.correct: <8}`\n"
            f"`{'Incorrect: ': <{padding_size}}{player.incorrect: <8}`\n"
            f"`{'Game Time: ': <{padding_size}}{game.get_game_duration(): <8}`\n"
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
