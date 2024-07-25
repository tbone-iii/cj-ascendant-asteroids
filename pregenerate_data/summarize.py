import datetime
import json
import secrets
import sys
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import openai

openai.api_key = sys.argv[1]
GPT_MODEL = "gpt-4"
NEWS_API_KEY = "589889c3716740ca8fc4c9c6413bac96"
NEWS_SITE_RSS_URL = "https://finance.yahoo.com/rss/"
TOOLONG_DEBUG_SIZE = 80
DEFAULT_TIMEZONE = ZoneInfo("America/Los_Angeles")

JSON_LOCATION = Path(__file__).resolve().parent / "articles.json"


class ArticleContextInfo:
    """Class info on article contexts."""

    def __init__(
        self,
        date: datetime.datetime | None = None,
        url: str = "",
        author: str = GPT_MODEL,
    ) -> None:
        if date is None:
            self.date = datetime.datetime.now(tz=DEFAULT_TIMEZONE)
        else:
            self.date = date

        self.url = url
        self.author = author


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
        sentence_options: list[str] = list[str] | None,
        incorrect_option: int = int | None,
    ) -> None:
        self.body_text = body_text
        self.summary = summary

        self.sentence_options = sentence_options
        self.incorrect_option = incorrect_option
        if self.sentence_options is None:
            self.sentence_options = []
            scanning = False
            for char in list(self.summary):
                if char in {"<", "["}:
                    if char == "[":
                        self.incorrect_option = len(self.sentence_options)

                    self.sentence_options.append("")
                    scanning = True

                elif char in {">", "]"}:
                    scanning = False

                elif scanning:
                    self.sentence_options[-1] += char


class Article:
    """Article full class."""

    def __init__(
        self,
        article_text_info: ArticleTextInfo,
        article_selection_info: ArticleSelectionInfo = None,
        article_context_info: ArticleContextInfo = None,
    ) -> None:
        self.article_text_info = article_text_info

        self.article_selection_info = article_selection_info
        if self.article_selection_info is None:
            self.article_selection_info = ArticleSelectionInfo()

        self.article_context_info = article_context_info
        if self.article_context_info is None:
            self.article_context_info = ArticleContextInfo()

    def __repr__(self) -> str:
        options_out = ""
        for num, sentence in enumerate(self.article_text_info.sentence_options):
            if num == self.article_text_info.incorrect_option:
                options_out += f"NOT TRUE -> {num}: {sentence}"
            else:
                options_out += f"{num}: {sentence}"

            if len(sentence) > TOOLONG_DEBUG_SIZE:
                options_out += " TOOLONG"

            options_out += "\n"

        return f"""
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
"""

    def write(self) -> None:
        """Add this article to the json file list of articles."""
        articles = Article.collect_articles()

        articles.append(
            {
                "body_text": self.article_text_info.body_text,
                "summary": self.article_text_info.summary,
                "questions": self.article_text_info.sentence_options,
                "incorrect_option": self.article_text_info.incorrect_option,
                "url": self.article_context_info.url,
                "topic": self.article_selection_info.topic,
                "size": self.article_selection_info.size,
                "date": f"{self.article_context_info.date.year}- \
                    {self.article_context_info.date.month}- \
                    {self.article_context_info.date.day}",
                "author": self.article_context_info.author,
            },
        )

        with Path.open(JSON_LOCATION, "w") as f:
            json.dump(articles, f)

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
                data["body_text"], data["summary"], data["sentence_options"], data["incorrect_option"],
            ),
            article_selection_info=ArticleSelectionInfo(data["topic"], data["size"]),
            article_context_info=ArticleContextInfo(
                date=datetime.datetime(year=year, month=month, day=day, tzinfo=DEFAULT_TIMEZONE),
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


def get_gpt_response(prompt_text: str) -> str:
    """Get a ChatGPT input and output."""
    response = openai.chat.completions.create(
        model=GPT_MODEL,
        messages=[
            {"role": "system", "content": prompt_text},
        ],
    )

    return response.choices[0].message.content or ""


def get_summary(article_body: str) -> str:
    """Get a summary from body text."""
    return get_gpt_response(
        "Please summarize the following article in around facts, \
            each fact sentence should be no longer than 10 words, \
            label 3 of these sentences with <> \
            (Please don't include bullet points or numbers in the brackets) \
            then add a sentence containing fake information, wrapped in [] instead\n \
            Please never but [] inside of <> or vise versa\n \
    "
        + article_body,
    )


article_body_text = get_gpt_response("Generate an article based on cats that is under 300 words")
article = Article(ArticleTextInfo(article_body_text, get_summary(article_body_text)))
article.write()
print(article)
