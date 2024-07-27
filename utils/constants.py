from enum import Enum


# Time specific constants
class DifficultyTimer(Enum):
    """Difficulty timer constants."""

    EASY = 60.0
    MEDIUM = 45.0
    HARD = 20.0


ARTICLE_TIMER = 60.0
EXTEND_TIMER_VALUE = 10.0

# Abilities specific constants
ABILITIES_THRESHOLD = 100
COOLDOWN_DURATION = 5.0
