import secrets
import time
from collections.abc import Callable
from enum import Enum

import discord


class AbilityType(Enum):
    """a class to represent abilities available to a player."""

    COOLDOWN = "Cooldown"
    REMOVE_QUESTION = "Remove Question"
    EXTEND_TIMER = "Extend Timer"

class Player:
    """A class to represent a player in the game.

    Attributes
    ----------
    player_id : int
        The unique ID of the player.
    name : str
        The name of the player.
    display_name : str
        The display name of the player.
    avatar_url : str
        The URL of the player's avatar.
    score : int
        The score of the player.
    abilities : list
        The list of abilities the player has.
    abilities_meter: int
        The value of the player's ability meter to determine when ability will appear.
    abilities_threshold: int
        The max value a player's ability meter will need to reach before an ability will appear.

    Methods
    -------
    add_ability(ability: AbilityType) -> None:
        Add an ability to the player's list of abilities.
    use_ability(ability: AbilityType) -> None:
        Use an ability.
    update_score(points: int) -> None:
        Update the player's score.
    get_display_name() -> str:
        Return the player's display name.
    get_avatar_url() -> str:
        Return the player's avatar URL.
    get_player_id() -> int:
        Return the player's ID.
    get_score() -> int:
        Return the player's score.
    get_abilities() -> list:
        Return the player's abilities.
    get_abilities_meter() -> int:
        Return the player's abilities meter.
    update_abilities_meter(value: int) -> None:
        Update the player's abilities meter.
    reset_abilities_meter() -> None:
        Reset the player's abilities meter.

    """

    def __init__(
        self,
        player_id: int,
        name: str,
        display_name: str,
        avatar_url: str,
    ) -> None:
        """Construct all the necessary attributes for the player object.

        Parameters
        ----------
        player_id : int
            The unique ID of the player.
        name : str
            The name of the player.
        display_name : str
            The display name of the player.
        avatar_url : str
            The URL of the player's avatar.

        """
        self.player_id = player_id
        self.name = name
        self.display_name = display_name
        self.avatar_url = avatar_url
        self.score = 0
        self.abilities = []
        self.abilities_meter = 0
        self.abilities_threshold = 100

    def add_ability(self, ability: AbilityType) -> None:
        """Add an ability to the player's list of abilities.

        Parameters
        ----------
        ability : AbilityType
            The ability to be added.

        """
        self.abilities.append(ability)

    def use_ability(self, ability: AbilityType) -> None:
        """Use an ability.

        Parameters
        ----------
        ability : AbilityType
            The ability to be used.

        """
        if ability in self.abilities:
            # Add cases for specific ability effects
            self.abilities.remove(ability)

    def update_score(self, points: int) -> None:
        """Update the player's score.

        Parameters
        ----------
        points : int
            The points to be added to the player's score.

        """
        self.score += points

    def get_display_name(self) -> str:
        """Return the player's display name.

        Returns
        -------
        str
            The display name of the player.

        """
        return self.display_name

    def get_avatar_url(self) -> str:
        """Return the player's avatar URL.

        Returns
        -------
        str
            The URL of the player's avatar.

        """
        return self.avatar_url

    def get_player_id(self) -> int:
        """Return the player's ID.

        Returns
        -------
        int
            The unique ID of the player.

        """
        return self.player_id

    def get_score(self) -> int:
        """Return the player's score.

        Returns
        -------
        int
            The score of the player.

        """
        return self.score

    def get_abilities(self) -> list:
        """Get the list of player's abilities."""
        return self.abilities

    def get_abilities_meter(self) -> int:
        """Get the value of player's ability meter."""
        return self.abilities_meter

    def update_abilities_meter(self, value: int) -> None:
        """Update the value of player's ability meter."""
        self.abilities_meter += value
        if self.abilities_meter >= self.abilities_threshold:
            self.abilities_meter = 0
            # Use secrets library to address Ruff linter's requests
            self.add_ability(secrets.choice(list(AbilityType)))

    def reset_abilities_meter(self) -> None:
        """Reset the abilities meter."""
        self.abilities_meter = 0

class Game:
    """A class to represent the game.

    Attributes
    ----------
    players : list
        The list of players in the game.
    state : str
        The current state of the game.
    start_time : float
        The start time in seconds.
    end_time: float
        The end time in seconds.

    Methods
    -------
    add_player(player: Player) -> None:
        Add a player to the game.
    start_game() -> None:
        Start the game by changing the state to 'in_progress'.
    end_game() -> None:
        End the game by changing the state to 'ended'.
    get_player(player_id: int) -> Player | None:
        Retrieve a player by their ID.
    create_start_game_embed(player: Player) -> discord.Embed:
        Create a Discord embed for the start of the game.
    get_game_duration() -> str:
        Return the duration of the game as a formatted string.

    """

    def __init__(self) -> None:
        """Construct all the necessary attributes for the game object."""
        self.players: list[Player] = []
        self.state = "not_started"
        self.start_time: float = 0.0
        self.end_time: float = 0.0

    def add_player(self, player: Player) -> None:
        """Add a player to the game.

        Parameters
        ----------
        player : Player
            The player to be added to the game.

        """
        self.players.append(player)

    def start_game(self) -> None:
        """Start the game by changing the state to 'in_progress'."""
        self.state = "in_progress"
        self.start_time = time.time()

    def end_game(self) -> None:
        """End the game by changing the state to 'ended'."""
        self.state = "ended"
        self.end_time = time.time()

    def get_player(self, player_id: int) -> "Player | None":
        """Retrieve a player by their ID.

        Parameters
        ----------
        player_id : int
            The unique ID of the player to be retrieved.

        Returns
        -------
        Player
            The player with the specified ID, or None if no player with the ID is found.

        """
        for player in self.players:
            if player.player_id == player_id:
                return player
        return None

    def create_start_game_embed(self, player: Player) -> discord.Embed:
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
        embed = discord.Embed(
            title="Welcome to Article Overload",
            color=discord.Color.green(),
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

    def get_game_duration(self) -> str:
        """Return the duration of the game as a formatted string."""
        if self.state != "ended":
            return "Game is still in progress."
        duration = self.end_time - self.start_time
        minutes, seconds = divmod(duration, 60)
        return f"{int(minutes)} minutes {int(seconds)} seconds"


class Ability:
    """A class to represent an ability.

    Attributes
    ----------
    name : str
        The name of the ability.
    description : str
        A description of what the ability does.
    cooldown_time : int
        The cooldown time for the ability in seconds.
    effect : function
        The function that defines the ability's effect.
    last_used : float
        The time when the ability was last used.

    Methods
    -------
    activate(user: 'Player', target: 'Player') -> bool:
        Activate the ability on a target.
    is_on_cooldown() -> bool:
        Check if the ability is on cooldown.
    time_left() -> float:
        Return the remaining cooldown time for the ability.

    """

    def __init__(
        self,
        name: str,
        description: str,
        cooldown_time: int,
        effect: Callable,
    ) -> None:
        """Construct all the necessary attributes for the ability object.

        Parameters
        ----------
        name : str
            The name of the ability.
        description : str
            A description of what the ability does.
        cooldown_time : int
            The cooldown time for the ability in seconds.
        effect : callable
            The function that defines the ability's effect.

        """
        self.name = name
        self.description = description
        self.cooldown_time = cooldown_time
        self.effect = effect
        self.last_used: float = 0.0

    def activate(self, user: "Player", target: "Player") -> bool:
        """Activate the ability on a target.

        Parameters
        ----------
        user : Player
            The player using the ability.
        target : Player
            The target player on whom the ability is being used.

        Returns
        -------
        bool
            True if the ability was successfully activated, False otherwise.

        """
        if self.is_on_cooldown():
            return False
        self.effect(user, target)
        self.last_used = time.time()
        return True

    def is_on_cooldown(self) -> bool:
        """Check if the ability is on cooldown.

        Returns
        -------
        bool
            True if the ability is on cooldown, False otherwise.

        """
        return time.time() - self.last_used < self.cooldown_time

    def time_left(self) -> float:
        """Return the remaining cooldown time for the ability.

        Returns
        -------
        float
            The remaining cooldown time in seconds.

        """
        return max(0, self.cooldown_time - (time.time() - self.last_used))
