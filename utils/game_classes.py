import time

import discord


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

    Methods
    -------
    add_ability(ability):
        Adds an ability to the player's list of abilities.
    use_ability(ability_name, target):
        Uses an ability on a target.
    update_score(points):
        Updates the player's score.
    get_display_name():
        Returns the player's display name.
    get_avatar_url():
        Returns the player's avatar URL.
    get_player_id():
        Returns the player's ID.
    get_score():
        Returns the player's score.

    """

    def __init__(self, player_id, name, display_name, avatar_url):
        """Constructs all the necessary attributes for the player object.

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

    def add_ability(self, ability):
        """Adds an ability to the player's list of abilities.

        Parameters
        ----------
        ability : Ability
            The ability to be added.

        """
        self.abilities.append(ability)

    def use_ability(self, ability_name, target):
        """Uses an ability on a target.

        Parameters
        ----------
        ability_name : str
            The name of the ability to be used.
        target : Player
            The target player on whom the ability will be used.

        Returns
        -------
        bool
            True if the ability was successfully used, False otherwise.

        """
        for ability in self.abilities:
            if ability.name == ability_name:
                return ability.activate(self, target)
        return False

    def update_score(self, points):
        """Updates the player's score.

        Parameters
        ----------
        points : int
            The points to be added to the player's score.

        """
        self.score += points

    def get_display_name(self):
        """Returns the player's display name.

        Returns
        -------
        str
            The display name of the player.

        """
        return self.display_name

    def get_avatar_url(self):
        """Returns the player's avatar URL.

        Returns
        -------
        str
            The URL of the player's avatar.

        """
        return self.avatar_url

    def get_player_id(self):
        """Returns the player's ID.

        Returns
        -------
        int
            The unique ID of the player.

        """
        return self.player_id

    def get_score(self):
        """Returns the player's score.

        Returns
        -------
        int
            The score of the player.

        """
        return self.score


class Game:
    """A class to represent the game.

    Attributes
    ----------
    players : list
        The list of players in the game.
    state : str
        The current state of the game.

    Methods
    -------
    add_player(player):
        Adds a player to the game.
    start_game():
        Starts the game.
    end_game():
        Ends the game.
    get_player(player_id):
        Retrieves a player by their ID.
    create_start_game_embed(player):
        Creates a Discord embed for the start of the game.

    """

    def __init__(self):
        """Constructs all the necessary attributes for the game object.
        """
        self.players = []
        self.state = "not_started"

    def add_player(self, player):
        """Adds a player to the game.

        Parameters
        ----------
        player : Player
            The player to be added to the game.

        """
        self.players.append(player)

    def start_game(self):
        """Starts the game by changing the state to 'in_progress'.
        """
        self.state = "in_progress"

    def end_game(self):
        """Ends the game by changing the state to 'ended'.
        """
        self.state = "ended"

    def get_player(self, player_id):
        """Retrieves a player by their ID.

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

    def create_start_game_embed(self, player):
        """Creates a Discord embed for the start of the game.

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
            title="Welcome to Article Overload", color=discord.Color.green(),
        )
        embed.add_field(name="Player ID", value=player.get_player_id(), inline=False)
        embed.add_field(
            name="Display Name", value=player.get_display_name(), inline=False,
        )
        embed.add_field(name="Score", value=player.get_score(), inline=False)
        embed.set_thumbnail(url=player.get_avatar_url())
        return embed


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
    activate(user, target):
        Activates the ability on a target.
    is_on_cooldown():
        Checks if the ability is on cooldown.
    time_left():
        Returns the remaining cooldown time for the ability.

    """

    def __init__(self, name, description, cooldown_time, effect):
        """Constructs all the necessary attributes for the ability object.

        Parameters
        ----------
        name : str
            The name of the ability.
        description : str
            A description of what the ability does.
        cooldown_time : int
            The cooldown time for the ability in seconds.
        effect : function
            The function that defines the ability's effect.

        """
        self.name = name
        self.description = description
        self.cooldown_time = cooldown_time
        self.effect = effect
        self.last_used = 0

    def activate(self, user, target):
        """Activates the ability on a target.

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

    def is_on_cooldown(self):
        """Checks if the ability is on cooldown.

        Returns
        -------
        bool
            True if the ability is on cooldown, False otherwise.

        """
        return time.time() - self.last_used < self.cooldown_time

    def time_left(self):
        """Returns the remaining cooldown time for the ability.

        Returns
        -------
        float
            The remaining cooldown time in seconds.

        """
        return max(0, self.cooldown_time - (time.time() - self.last_used))
