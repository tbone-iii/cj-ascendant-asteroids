from dataclasses import dataclass
from enum import Enum

from discord import Color


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

SCORE_BOARD_SPACING_SIZE = 20
SCORE_BOARD_NUM_SCORES_TO_SHOW = 10
SCORE_BOARD_COLOR = Color.gold()


@dataclass(frozen=True)
class ImageURLs:
    """Track all image URLs and assets used here in a single location."""

    ANIMATED_TROPHY = "https://cdn.pixabay.com/animation/2023/06/13/15/13/15-13-22-874_256.gif"
