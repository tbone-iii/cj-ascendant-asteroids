from dataclasses import dataclass
from enum import Enum
from os import environ

from discord import Color, Intents
from dotenv import load_dotenv

load_dotenv()


# Discord bot constants
TOKEN: str | None = environ.get("TOKEN")

COLORS: dict[str, str] = {
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "default": "\033[37m",
}

COLOR_MAIN: int = 0xCEB512
COLOR_GOOD: int = 0x0AE636
COLOR_NEUTRAL: int = 0xD9DD0E
COLOR_BAD: int = 0xF00000

OWNER_IDS: list[int] = [
    239810885093294080,
    250742565257740290,
    756154615938154637,
    629447010839166976,
    617892283949383681,
]

NEWS_STATIONS: list[str] = ["ANC", "BBC", "CBS", "CNN", "Fox News", "Reddit"]

INTENTS: Intents = Intents(message_content=True)

IGNORE_FILES = ["__init__.py"]


# Game constants
CORRECT_ANSWER_POINTS = 10
INCORRECT_ANSWER_POINTS = 5
MAX_INCORRECT = 3


# Time specific constants
class DifficultyTimer(Enum):
    """Difficulty timer constants."""

    EASY = 60.0
    MEDIUM = 45.0
    HARD = 20.0


# Abilities specific constants
ABILITIES_THRESHOLD = 100
COOLDOWN_DURATION = 5.0
EXTEND_TIMER_VALUE = 10.0


# Display constants
SCORE_BOARD_SPACING_SIZE = 20
SCORE_BOARD_NUM_SCORES_TO_SHOW = 10
SCORE_BOARD_COLOR = Color.gold()
ABSOLUTE_CHAR_LIMIT = 100
RELATIVE_CHAR_LIMIT = 97
DIGIT_TO_EMOJI = {
    1: "1️⃣",
    2: "2️⃣",
    3: "3️⃣",
    4: "4️⃣",
    5: "5️⃣",
    6: "6️⃣",
    7: "7️⃣",
    8: "8️⃣",
    9: "9️⃣",
}


# Image constants
@dataclass(frozen=True)
class ImageURLs:
    """Track all image URLs and assets used here in a single location."""

    SUCCESS = "https://media3.giphy.com/media/CaS9NNso512WJ4po0t/giphy.gif?cid=ecf05e47mgm8u6fljfxl5d5g0s01tp94qgn9exfwqvlpi3id&rid=giphy.gif&ct=s"
    WARNING = "https://c.tenor.com/26pNa498OS0AAAAi/warning-joypixels.gif"
    NO_FINGER = "https://cdn.pixabay.com/animation/2022/11/03/15/02/15-02-00-156_256.gif"
    ERROR = "https://i.gifer.com/origin/bf/bf2d25254a2808835e20c9d698d75f28_w200.gif"
    ANIMATED_TROPHY = "https://cdn.pixabay.com/animation/2023/06/13/15/13/15-13-22-874_256.gif"
    NOT_ALLOWED_SIGN = "https://cdn.pixabay.com/animation/2022/12/21/03/47/03-47-43-799_256.gif"
