import inspect
from dataclasses import dataclass
from typing import Any, Protocol, Self


class ObjectMixin(Protocol):
    """Mixin class for client-facing objects."""

    @classmethod
    def from_dict(cls, mapping: dict) -> Self:
        """Generate an object from a dictionary, stripping out any extra keys not relevant to the class."""
        return cls(**{k: v for k, v in mapping.items() if k in inspect.signature(cls).parameters})

    def get_dict(self) -> dict[str, Any]:
        """Return only non-None attributes as a dictionary."""
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass
class Article(ObjectMixin):
    """Client-facing Article object (not to be confused with the ORM Article model)."""

    id: int | None = None
    url: str | None = None
    body_text: str | None = None
    summary: str | None = None
