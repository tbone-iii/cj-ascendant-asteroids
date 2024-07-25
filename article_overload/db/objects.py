"""Objects are based upon the ORM models based on classes provided by SQL alchemy."""

from typing import Self

from pydantic import BaseModel

from article_overload.db.models import ArticleRecord
from article_overload.exceptions import DatabaseObjectNotProperlyInitializedError


class Article(BaseModel):
    """Article object to reference elements within the JSON structure.

    This object is NOT used to interact with the database. It is strictly used within the context of the JSON file.
    # summary: list[str]
    # fake_fact: list[str]
    # title: str
    # topic: str
    # size: str
    # author: str
    # date_published: datetime
    """

    id: int | None = None
    url: str
    body_text: str
    summary: str

    @classmethod
    def create_from_article_record(cls, article_record: ArticleRecord) -> Self:
        """Create an Article object from an ArticleRecord object.

        :Return: `Article`
        """
        return cls(
            id=article_record.id,
            url=article_record.url,
            body_text=article_record.body_text,
            summary=article_record.summary,
        )

    def create_article_record(self) -> ArticleRecord:
        """Create an ArticleRecord object from the current Article object.

        :Return: `ArticleRecord`
        """
        return ArticleRecord(
            url=self.url,
            body_text=self.body_text,
            summary=self.summary,
        )

    def update_id_from_article_record(self, article_record: ArticleRecord) -> Self:
        """Update Article from an ArticleRecord object.

        :Return: `Article`
        """
        if article_record.id is None:
            raise DatabaseObjectNotProperlyInitializedError

        self.id = article_record.id

        return self
