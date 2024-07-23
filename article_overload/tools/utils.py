import json
from pathlib import Path

from discord import Embed

from article_overload.constants import COLOR_BAD, COLOR_GOOD, COLOR_NEUTRAL, COLORS


def color_message(message: str, color: str = COLORS["default"]) -> str:
    """Color message function.

    Description: Adds color to a message in console.
    :Return: String
    """
    return COLORS.get(color, COLORS["default"]) + message + "\033[0m"


def create_success_embed(title: str = "\u200b", description: str = "\u200b") -> Embed:
    """Embed creator.

    Description: Creates a success embed.
    :Return: Embed
    """
    embed = Embed(title=title, description=description, color=COLOR_GOOD)
    embed.set_thumbnail(
        url="https://media3.giphy.com/media/CaS9NNso512WJ4po0t/giphy.gif?cid=ecf05e47mgm8u6fljfxl5d5g0s01tp94qgn9exfwqvlpi3id&rid=giphy.gif&ct=s",
    )
    return embed


def create_warning_embed(title: str = "\u200b", description: str = "\u200b") -> Embed:
    """Embed creator.

    Description: Creates a warning embed.
    :Return: Embed
    """
    embed = Embed(title=title, description=description, color=COLOR_NEUTRAL)
    embed.set_thumbnail(
        url="https://c.tenor.com/26pNa498OS0AAAAi/warning-joypixels.gif",
    )
    return embed


def create_error_embed(title: str = "\u200b", description: str = "\u200b") -> Embed:
    """Embed creator.

    Description: Creates an error embed.
    :Return: Embed
    """
    embed = Embed(title=title, description=description, color=COLOR_BAD)
    embed.set_thumbnail(
        url="https://i.gifer.com/origin/bf/bf2d25254a2808835e20c9d698d75f28_w200.gif",
    )
    return embed


def get_json_file(file_path: str) -> dict:
    """JSON file reader.

    Description: Reads a json file.
    :Return: Dict
    """
    path = Path(file_path)
    with path.open("r") as f:
        return json.load(f)


def update_json_file(data: dict, file_path: str) -> None:
    """JSON file updater.

    Description: Updates contents of a json file.
    :Return: None
    """
    path = Path(file_path)
    with path.open("w") as f:
        json.dump(data, f)


def read_text_file(file_path: str) -> str:
    """Text file reader.

    Description: Reads a text file.
    :Return: String
    """
    path = Path(file_path)
    with path.open("r") as f:
        return f.read()
