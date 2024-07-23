
import time

class Ability:
    def __init__(self, name, description, cooldown_time, effect):
        self.name = name
        self.description = description
        self.cooldown_time = cooldown_time
        self.effect = effect
        self.last_used = 0

    def activate(self, user, target):
        if self.is_on_cooldown():
            return False
        self.effect(user, target)
        self.last_used = time.time()
        return True

    def is_on_cooldown(self):
        return time.time() - self.last_used < self.cooldown_time

    def time_left(self):
        return max(0, self.cooldown_time - (time.time() - self.last_used))

class Player:
    def __init__(self, player_id, name, display_name, avatar_url):
        self.player_id = player_id
        self.name = name
        self.display_name = display_name
        self.avatar_url = avatar_url
        self.score = 0
        self.abilities = []

    def add_ability(self, ability):
        self.abilities.append(ability)

    def use_ability(self, ability_name, target):
        for ability in self.abilities:
            if ability.name == ability_name:
                return ability.activate(self, target)
        return False

    def update_score(self, points):
        self.score += points

    def get_display_name(self):
        return self.display_name

    def get_avatar_url(self):
        return self.avatar_url

    def get_player_id(self):
        return self.player_id

    def get_score(self):
        return self.score

class Game:
    def __init__(self):
        self.players = []
        self.state = "not_started"

    def add_player(self, player):
        self.players.append(player)

    def start_game(self):
        self.state = "in_progress"

    def end_game(self):
        self.state = "ended"

    def get_player(self, player_id):
        for player in self.players:
            if player.player_id == player_id:
                return player
        return None

    def start_game_message(self, player):
        return (f"=== Article Overload ===\n"
                f"Player:\n"
                f"{player.get_player_id()}\n"
                f"{player.get_display_name()}\n"
                f"{player.get_avatar_url()}\n"
                f"Score: {player.get_score()}")
