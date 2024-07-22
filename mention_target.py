from enum import Enum


class MentionTarget(Enum):
    """Enum for the target of a mention. The string values are descriptions."""

    EVERYONE = "everyone"  # @everyone
    NONE = ""  # No mention
