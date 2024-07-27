"""Objects are based upon the ORM models based on classes provided by SQL alchemy."""

from datetime import datetime
from re import sub
from typing import Self

from pydantic import BaseModel, computed_field

from article_overload.db.models import ArticleRecord, QuestionRecord, SizeRecord
from article_overload.exceptions import DatabaseObjectNotProperlyInitializedError


class Article(BaseModel):
    """Article object to reference elements within the JSON structure.

    This object is used by the client to store the user-friendly data from the database.
    """

    id: int | None = None
    url: str
    body_text: str
    summary: str
    questions: list[str]
    incorrect_option_index: int
    title: str
    topic: str
    size: str
    author: str
    date_published: datetime

    @computed_field  # type: ignore[misc]
    @property
    def false_statement(self) -> str:
        """Return the incorrect question from the list of questions.

        :Return: `str`
        """
        return self.questions[self.incorrect_option_index]

    @computed_field  # type: ignore[misc]
    @property
    def true_statements(self) -> list[str]:
        """Return a list of correct statements from the list of questions.

        :Return: `list[str]`
        """
        return [question for index, question in enumerate(self.questions) if index != self.incorrect_option_index]

    @computed_field
    @property
    def marked_up_summary(self) -> str:
        """Return the marked up version of the summary text (version containing the sentence options bolded).

        :Return: `str`
        """
        marked_up_text = ""
        n = 0
        for sentence in sub(r"[<>[\]]", "", self.summary).splitlines():
            if sentence.strip() in self.questions:
                n += 1
                marked_up_text += f"**`{n}. {sentence.strip()}`** "

            else:
                marked_up_text += sentence.strip().strip('"') + " "

        return marked_up_text[:-1]

    @computed_field
    @property
    def highlight_answer_in_summary(self) -> str:
        """Return the summary text with the false statement bolded with the other statements striked out.

        :Return: `str`
        """
        marked_up_text = self.marked_up_summary

        for index, sentence in enumerate(self.questions):
            if sentence in self.true_statements:
                marked_up_text = marked_up_text.replace(f"**`{index+1}. {sentence}`**", f"~~`{index+1}. {sentence}`~~")

        return marked_up_text

    @classmethod
    def create_from_article_record(
        cls,
        article_record: ArticleRecord,
        question_records: list[QuestionRecord],
        size_record: SizeRecord,
    ) -> Self:
        """Create an Article object from an ArticleRecord object.

        :Return: `Article`
        """
        questions = [record.question for record in question_records]

        return cls(
            id=article_record.id,
            url=article_record.url,
            body_text=article_record.body_text,
            questions=questions,
            summary=article_record.summary,
            incorrect_option_index=article_record.incorrect_option_index,
            title=article_record.title,
            topic=article_record.topic,
            size=size_record.size,
            author=article_record.author,
            date_published=article_record.date_published,
        )

    def create_article_record(self, size_record: SizeRecord) -> ArticleRecord:
        """Create an ArticleRecord object from the current Article object.

        :Return: `ArticleRecord`
        """
        question_records = [QuestionRecord(question=question) for question in self.questions]

        return ArticleRecord(
            url=self.url,
            body_text=self.body_text,
            questions=question_records,
            summary=self.summary,
            incorrect_option_index=self.incorrect_option_index,
            title=self.title,
            topic=self.topic,
            size_id=size_record.id,
            author=self.author,
            date_published=self.date_published,
        )

    def update_id_from_article_record(self, article_record: ArticleRecord) -> Self:
        """Update Article from an ArticleRecord object.

        :Return: `Article`
        """
        if article_record.id is None:
            raise DatabaseObjectNotProperlyInitializedError

        self.id = article_record.id

        return self


class ArticleResponse(BaseModel):
    """Article response object used to interface with the ORM data structure.

    This object is used by the client to store the user-friendly data from the database.
    """

    user_id: int
    session_id: int
    response: str
    is_correct: bool
