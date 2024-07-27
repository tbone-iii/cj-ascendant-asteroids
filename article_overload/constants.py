from os import environ

from discord import Intents
from dotenv import load_dotenv

load_dotenv()

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

CORRECT_ANSWER_POINTS = 10
INCORRECT_ANSWER_POINTS = 5
MAX_INCORRECT = 3
