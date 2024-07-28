from dataclasses import dataclass

from article_overload.constants import ABSOLUTE_CHAR_LIMIT

from .sentence_type import SentenceType


@dataclass
class Sentence:
    """Basic dataclass for the sentence object."""

    text: str
    sentence_type: SentenceType

    def get_truncated_text(self, prefix: str = "", suffix: str = "...") -> str:
        """Get the truncated text with a prefix and suffix."""
        adjusted_limit = ABSOLUTE_CHAR_LIMIT - len(prefix) - len(suffix)
        text = self.text
        if len(text) > adjusted_limit:
            text = text[:adjusted_limit]
            return f"{prefix}{text}{suffix}"
        return f"{prefix}{text}"

    def formatted_sentence_hidden(self, number: int | None) -> str:
        """Return the sentence text formatted for Discord to hide the sentence types from the user.

        If the number is provided, the sentence will be formatted with a number.
        """
        if number is None:
            return self.text

        return f"`{number}. {self.text}`"

    def formatted_sentence_result(self, number: int | None = None) -> str:
        """Return the sentence text formatted for Discord to reveal the sentence types to the user.

        If the number is provided, the sentence will be formatted with a number.
        """
        if number is None:
            return self.text

        number_string = f"{number}. "
        if self.sentence_type == SentenceType.TRUE:
            return f"**`{number_string}{self.text}`**"

        return f"~~`{number_string}{self.text}`~~"
