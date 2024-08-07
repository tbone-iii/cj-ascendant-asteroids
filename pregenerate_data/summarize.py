import datetime
import json
import os
import secrets
from datetime import UTC
from inspect import cleandoc
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
NEWS_SITE_RSS_URL = "https://finance.yahoo.com/rss/"
TOOLONG_DEBUG_SIZE = 80

DEFAULT_TIMEZONE = UTC

JSON_LOCATION = Path(__file__).resolve().parent / "articles.json"


class ArticleContextInfo:
    """Class info on article contexts."""

    def __init__(
        self,
        title: str = "Unnamed Article",
        date: datetime.datetime | None = None,
        url: str = "",
        author: str = "gpt",
    ) -> None:
        if date is None:
            self.date = datetime.datetime.now(tz=DEFAULT_TIMEZONE)
        else:
            self.date = date

        self.url = url
        self.author = author
        self.title = title


class ArticleSelectionInfo:
    """Class info on article selection from the user."""

    def __init__(self, topic: str = "General", size: str = "Small") -> None:
        self.topic = topic
        self.size = size


class ArticleTextInfo:
    """Class info on article body and summary."""

    def __init__(
        self,
        body_text: str,
        summary: str,
        sentence_options: list[str] | None = None,
        incorrect_option: int | None = None,
    ) -> None:
        self.body_text = body_text
        self.summary = summary

        self.sentence_options = sentence_options
        self.incorrect_option = incorrect_option
        if isinstance(self.sentence_options, list):
            return

        self.build_sentence_options(summary)

    def build_sentence_options(self, summary: str) -> None:
        """Build the sentence options."""
        self.sentence_options = []
        self.incorrect_option = None

        sentences = [sentence for sentence in summary.split("\n") if sentence]
        counter = 0
        for sentence in sentences:
            if sentence.startswith("[") and sentence.endswith("]"):
                if self.incorrect_option is not None:
                    self.incorrect_option = None
                    return
                self.incorrect_option = counter
                self.sentence_options.append(sentence.removeprefix("[").removesuffix("]"))
                continue
            if sentence.startswith("<") and sentence.endswith(">"):
                self.sentence_options.append(sentence.removeprefix("<").removesuffix(">"))
                counter += 1
                continue


class Article:
    """Article full class."""

    def __init__(
        self,
        article_text_info: ArticleTextInfo,
        article_selection_info: ArticleSelectionInfo | None = None,
        article_context_info: ArticleContextInfo | None = None,
    ) -> None:
        self.article_text_info = article_text_info
        self.article_selection_info = article_selection_info or ArticleSelectionInfo()
        self.article_context_info = article_context_info or ArticleContextInfo()

    def __repr__(self) -> str:
        options_out = ""

        sentence_options = self.article_text_info.sentence_options or []
        for num, sentence in enumerate(sentence_options):
            if num == self.article_text_info.incorrect_option:
                options_out += f"NOT TRUE -> {num}: {sentence}"
            else:
                options_out += f"{num}: {sentence}"

            if len(sentence) > TOOLONG_DEBUG_SIZE:
                options_out += " TOOLONG"

            options_out += "\n"

        return cleandoc(f"""
            ----- {self.article_context_info.title} -----
            ----- INFO -----
            Topic: {self.article_selection_info.topic}
            Size: {self.article_selection_info.size}
            Date: {self.article_context_info.date}
            URL: {self.article_context_info.url}
            Author: {self.article_context_info.author}
            ----- TEXT BODY START -----
            {self.article_text_info.body_text}
            ----- TEXT BODY END -----

            ----- SUMMARY START -----
            {self.article_text_info.summary}
            ----- SUMMARY END -----

            ----- OPTIONS START -----
            {options_out}
            ----- OPTIONS END -----
        """)

    def write(self) -> None:
        """Add this article to the json file list of articles."""
        articles = Article.collect_articles()

        sentence_options = self.article_text_info.sentence_options or []
        print(len(sentence_options))

        year = self.article_context_info.date.year
        month = self.article_context_info.date.month
        day = self.article_context_info.date.day
        articles.append(
            {
                "title": self.article_context_info.title,
                "body_text": self.article_text_info.body_text,
                "summary": self.article_text_info.summary,
                "questions": self.article_text_info.sentence_options,
                "incorrect_option_index": self.article_text_info.incorrect_option,
                "url": self.article_context_info.url,
                "topic": self.article_selection_info.topic,
                "size": self.article_selection_info.size,
                "date_published": f"{year}-{month}-{day}",
                "author": self.article_context_info.author,
            },
        )

        with Path.open(JSON_LOCATION, "w") as f:
            json.dump(articles, f, indent=4)

    @staticmethod
    def collect_articles() -> list[dict]:
        """Collect all articles jsons from file."""
        with Path.open(JSON_LOCATION) as f:
            data = json.load(f)
            return list(data)

    @staticmethod
    def create_article_with_json(data: dict[str, Any]) -> "Article":
        """Create an instance of Article with the given json data."""
        year, month, day = data["date"].split("-")
        return Article(
            article_text_info=ArticleTextInfo(
                data["body_text"],
                data["summary"],
                data["questions"],
                data["incorrect_option"],
            ),
            article_selection_info=ArticleSelectionInfo(data["topic"], data["size"]),
            article_context_info=ArticleContextInfo(
                title=data["title"],
                date=datetime.datetime(year=int(year), month=int(month), day=int(day), tzinfo=DEFAULT_TIMEZONE),
                url=data["url"],
                author=data["author"],
            ),
        )

    @staticmethod
    def pick_random() -> "Article":
        """Pick and return a random Article type from the json saved list."""
        articles = Article.collect_articles()
        picked_article = secrets.choice(articles)
        return Article.create_article_with_json(picked_article)
