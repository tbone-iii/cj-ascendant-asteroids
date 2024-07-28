import secrets, time, random
from enum import Enum

from article_overload.constants import CORRECT_ANSWER_POINTS, INCORRECT_ANSWER_POINTS
from article_overload.log import our_logger
from discord.ext import tasks
from .log import our_logger

from article_overload.constants import (
    ABILITIES_THRESHOLD,
    COOLDOWN_DURATION,
    CORRECT_ANSWER_POINTS,
    INCORRECT_ANSWER_POINTS,
    EXTEND_TIMER_VALUE,
)


def ability_cooldown(player: "Player", game_view: "GameView") -> None:  # NOQA: F821
    """Run a callback for a button."""
    our_logger.info(f"{player.display_name} used the cooldown ability.")


def ability_remove_question(player: "Player", game_view: "GameView") -> None:  # NOQA: F821
    """Run a callback for a button."""
    # Pick a random number and pop it from the selectview
    print(game_view.sentence_picker.options)
    sentence_count = len(game_view.sentence_picker.options)
    idx = random.randint(0, sentence_count-1)
    while game_view.sentence_picker.options[idx-1].label[3::] in game_view.article_handler.false_sentence.text:
        idx = secrets.randbelow(sentence_count)
    print(game_view.sentence_picker.options.pop(idx))
    our_logger.info(f"{player.display_name} used the remove questions ability.")


def ability_extend_timer(player: "Player", game_view: "GameView") -> None:  # NOQA: F821
    """Run a callback for a button."""
    if player.game.get_article_timer() <= 0:
        result = f"{player.display_name} attempted to use ability_cooldown. Nothing to cool down!"
    else:
        # Changes start time according to coldown duration
        player.game.article_timer_start += EXTEND_TIMER_VALUE
        game_view.round_end_time += int(EXTEND_TIMER_VALUE)
        result = (
            f"{player.display_name} used the extend timer ability. Timer increased by {EXTEND_TIMER_VALUE} seconds."
        )
    our_logger.info(result)


class AbilityType(Enum):
    """a class to represent abilities available to a player."""

    COOLDOWN = (ability_cooldown,)
    REMOVE_QUESTION = (ability_remove_question,)
    EXTEND_TIMER = (ability_extend_timer,)


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
    get_abilities_meter_percentage -> int:
        Get the player's ability meter capacity in %
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
        self.game: Game | None = None
        self.player_id = player_id
        self.name = name
        self.display_name = display_name
        self.avatar_url = avatar_url
        self.score = 0
        self.correct = 0
        self.incorrect = 0
        self.answer_streak = 0
        self.abilities: list[AbilityType] = []
        self.abilities_meter = 0
        self.abilities_threshold = ABILITIES_THRESHOLD
        self.all_time_score: int = 0

    def add_ability(self, ability: AbilityType) -> None:
        """Add an ability to the player's list of abilities.

        Parameters
        ----------
        ability : AbilityType
            The ability to be added.

        """
        self.abilities.append(ability)

    def use_ability(self, ability: AbilityType, game: "Game") -> str:
        """Use an ability."""
        if ability not in self.abilities:
            return "Ability not found!"

        result = ""
        if ability == AbilityType.COOLDOWN:
            if game.article_timer <= 0:
                result = "Nothing to cool down!"
            else:
                game.article_timer -= COOLDOWN_DURATION
                result = f"Cooldown ability used! Timer reduced by {COOLDOWN_DURATION} seconds."

        elif ability == AbilityType.EXTEND_TIMER:
            if game.get_article_timer() <= 0:
                result = "Nothing to extend!"
            else:
                game.article_timer_start = game.article_timer
                result = f"Extend Timer ability used! Timer reset to {game.article_timer} seconds."

        elif ability == AbilityType.REMOVE_QUESTION:
            result = "Remove Question ability used! (Effect TBD)"

        self.abilities.remove(ability)
        return result

    def update_score(self, points: int) -> None:
        """Update the player's score.

        Parameters
        ----------
        points : int
            The points to be added to the player's score.

        """
        self.score += points

    def add_correct(self) -> None:
        """Add points for correct answer and update streaks."""
        self.score += CORRECT_ANSWER_POINTS
        self.correct += 1
        self.answer_streak += 1
        self.update_abilities_meter(value=20)

    def add_incorrect(self) -> None:
        """Remove points for incorrect answer and update streaks."""
        self.score -= INCORRECT_ANSWER_POINTS
        self.incorrect += 1
        self.answer_streak = 0

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

    @tasks.loop(seconds=5)
    async def async_loop_abilities_meter(self, value: int = 15) -> AbilityType | None:
        """Update the abilities meter every 5 seconds."""
        self.abilities_meter += value
        our_logger.info(f"Abilities meter value: {self.abilities_meter}")
        if self.abilities_meter >= self.abilities_threshold:
            self.reset_abilities_meter()
            new_ability = secrets.choice(list(AbilityType))
            our_logger.info(f"New ability, [{new_ability}] added!")
            self.add_ability(new_ability)
            return new_ability
        return None

    def update_abilities_meter(self, value: int) -> AbilityType | None:
        """Update the abilities meter and return the new ability if threshold is reached."""
        self.abilities_meter += value
        print(f"Abilities_meter value: {self.abilities_meter}")
        if self.abilities_meter >= self.abilities_threshold:
            self.reset_abilities_meter()
            new_ability = secrets.choice(list(AbilityType))
            print(f"Ability [{new_ability}] added!")
            self.add_ability(new_ability)
            return new_ability
        return None

    def get_abilities_meter_percentage(self) -> int:
        """Get the meter percentage obtained and return its value."""
        return int((self.abilities_meter / self.abilities_threshold) * 100)

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
        # Game specific timing
        self.start_time: float = 0.0
        self.end_time: float = 0.0
        # Article specific timing, capped 15 second allowed per question
        self.article_timer: float = 0.0
        self.article_timer_start: float = 0.0
        self.article_timer_active: bool = False
        # Metadata tracking for the game
        self.user_id_to_session_id: dict[int, int] = {}

    @property
    def player_ids(self) -> list[int]:
        """The IDs of the players in the game."""
        return [player.player_id for player in self.players]

    def add_player(self, player: Player) -> None:
        """Add a player to the game.

        Parameters
        ----------
        player : Player
            The player to be added to the game.

        """
        player.game = self
        self.players.append(player)

    def add_session_id_for_player(self, player: Player, session_id: int) -> None:
        """Add a session ID for a player to the game."""
        self.user_id_to_session_id.update({player.player_id: session_id})

    def get_session_id_for_player(self, player: Player) -> int | None:
        """Get the session ID for a player."""
        return self.user_id_to_session_id.get(player.player_id, None)

    def start_game(self, article_timer: float) -> None:
        """Start the game by changing the state to 'in_progress'."""
        self.state = "in_progress"
        self.start_time = time.time()
        self.article_timer = article_timer

    def end_game(self) -> None:
        """End the game by changing the state to 'ended'."""
        self.state = "ended"
        self.end_time = time.time()
        self.players[0].async_loop_abilities_meter.cancel()

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

    def get_game_duration(self) -> str:
        """Return the duration of the game as a formatted string."""
        if self.state == "not_started":
            return "Game has not started."

        duration = time.time() - self.start_time
        minutes, seconds = divmod(duration, 60)
        return f"{int(minutes)}m {int(seconds)}s"

    def start_article_timer(self) -> None:
        """Start the timer countdown for the overload article questions."""
        self.article_timer_start = time.time()
        self.article_timer_active = True


    def stop_article_timer(self) -> None:
        """Stop the timer countdown for the overload article questions."""
        self.article_timer_active = False
        self.players[0].async_loop_abilities_meter.cancel()

    def get_article_timer(self) -> float:
        """Get the timer countdown for the overload article questions."""
        if self.article_timer_active:
            elapsed = time.time() - self.article_timer_start
            return max(0, self.article_timer - elapsed)
        return 0
