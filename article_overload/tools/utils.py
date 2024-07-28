import json
from pathlib import Path

from article_overload.constants import COLORS


def color_message(message: str, color: str = COLORS["default"]) -> str:
    """Color message function.

    Description: Adds color to a message in console.
    :Return: String
    """
    return COLORS.get(color, COLORS["default"]) + message + "\033[0m"


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
