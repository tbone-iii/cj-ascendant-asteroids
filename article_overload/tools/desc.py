from enum import Enum


class CommandDescriptions(Enum):
    """Command Descriptions Class."""

    PING = "Check the ping of the bot"
    CREATE_EMBED = "Generates an embed and sends it"
    CREATE_BUTTON_EXAMPLE = "Creates a view from ButtonViews containing buttons."
    GREET = "Greets the server with the option to mention `everyone`."
    CONFIRM_DENY = "Sends an embed containing a confirm/deny view"
    USER_INPUT = "Gets input from a user"
    SELECT_STUFF = "Enables user to select from select menu"
    PAGINATION = "Flip through pages"
    GAME_START = "Starts the game."
    GAME_END = "Ends the game."


class CommandOptionDescriptions(Enum):
    """Command Option Descriptions Class."""
