import json, requests
from typing import Union
from ..constants import COLORS, COLOR_GOOD, COLOR_NEUTRAL, COLOR_BAD, OWNER_IDS
from discord import Embed, Member, Role


def color_message(message: str, color: str = COLORS["default"]):
    color = COLORS.get(color, COLORS["default"])
    return color + message + "\033[0m"


def create_success_embed(title: str = "\u200b", description: str = "\u200b"):
    embed = Embed(title=title, description=description, color=COLOR_GOOD)
    embed.set_thumbnail(
        url="https://media3.giphy.com/media/CaS9NNso512WJ4po0t/giphy.gif?cid=ecf05e47mgm8u6fljfxl5d5g0s01tp94qgn9exfwqvlpi3id&rid=giphy.gif&ct=s"
    )
    return embed


def create_warning_embed(title: str = "\u200b", description: str = "\u200b"):
    embed = Embed(title=title, description=description, color=COLOR_NEUTRAL)
    embed.set_thumbnail(
        url="https://c.tenor.com/26pNa498OS0AAAAi/warning-joypixels.gif"
    )
    return embed


def create_error_embed(title: str = "\u200b", description: str = "\u200b"):
    embed = Embed(title=title, description=description, color=COLOR_BAD)
    embed.set_thumbnail(
        url="https://i.gifer.com/origin/bf/bf2d25254a2808835e20c9d698d75f28_w200.gif"
    )
    return embed


def check_perms(item: Union[Member, Role, str]):
    if not item:
        return False

    try:
        if item.id in OWNER_IDS:
            return True

    except:
        pass

    with open("./bot_data/perms.json") as f:
        perms = json.load(f)

    try:
        if item.id in perms["discordperms"]:
            return True

        for i in item.members:
            if i.id not in perms["discordperms"]:
                return False

        return True

    except:
        return False


def send_webhook_message(
    url: str,
    username: str,
    content: str = None,
    embed: dict = None,
    avatarURL: str = None,
):
    requests.post(
        url,
        json={
            "content": content,
            "username": username,
            "embeds": [embed] if embed else None,
            "avatar_url": avatarURL if avatarURL else None,
        },
    )


def get_json_file(path: str):
    with open(path) as f:
        data = json.load(f)

    return data


def update_json_file(data: dict, path: str):
    with open(path, "w") as f:
        json.dump(data, f)


def read_text_file(path: str):
    with open(path) as f:
        return f.read()
