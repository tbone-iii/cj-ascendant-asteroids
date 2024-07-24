import datetime
import json
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

import openai
import secret

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
    """Class info on article body and summery."""

    def __init__(self, body_text: str, summery: str) -> None:
        self.body_text = body_text
        self.summery = summery


class Article:
    """Article full class."""

    def __init__(
        self,
        article_text_info: ArticleTextInfo,
        article_selection_info: ArticleSelectionInfo,
        article_context_info: ArticleContextInfo,
    ) -> None:
        self.article_text_info = article_text_info
        self.article_selection_info = article_selection_info
        self.article_context_info = article_context_info

        self.sentence_options = []

        scanning = False
        for char in list(self.article_text_info.summery):
            if char in ("<", "["):
                if char == "[":
                    self.incorrect_option = len(self.sentence_options)

                self.sentence_options.append("")
                scanning = True

            elif char in (">", "]"):
                scanning = False

            elif scanning:
                self.sentence_options[-1] += char

    def __repr__(self) -> str:
        options_out = ""
        for num, sentence in enumerate(self.sentence_options):
            if num == self.incorrect_option:
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

----- SUMMERY START -----
{self.article_text_info.summery}
----- SUMMERY END -----

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
                "summery": self.article_text_info.summery,
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
    def collect_articles() -> dict:
        """Collect all articles jsons from file."""
        with Path.open(JSON_LOCATION) as f:
            data = json.load(f)
            return list(data)

    @staticmethod
    def create_article_with_json(data: json) -> "Article":
        """Create an instance of Article with the given json data."""
        return Article(
            data["body_text"],
            data["summery"],
            data["topic"],
            data["size"],
            datetime.datetime(data["date"], tzinfo=DEFAULT_TIMEZONE),
            data["url"],
            data["author"],
        )

    @staticmethod
    def pick_random() -> "Article":
        """Pick and return a random Article type from the json saved list."""
        articles = Article.collect_articles()
        picked_article = secret.choice(articles)
        return Article.create_article_with_json(picked_article)


def get_gpt_response(prompt_text: str) -> str:
    """Get a chatGPT input and output."""
    response = openai.chat.completions.create(
        model=GPT_MODEL,
        messages=[
            {"role": "system", "content": prompt_text},
        ],
    )

    return response.choices[0].message.content


def get_summery(article_body: str) -> str:
    """Get a summary from body text."""
    return get_gpt_response(
        "Please summarize the following article in around facts, \
            each fact sentence should be no longer than 10 words, \
            label 3 of these sentces with <> \
            (Please don't include bullet points or numbers in the brackets) \
            then add a sentence containing fake information, wrapped in [] instead\n \
            Please never but [] inside of <> or vise versa\n \
    "
        + article_body,
    )


article_body_text = get_gpt_response("Generate an article based on cats that is under 300 words")
article = Article(
    ArticleTextInfo(article_body_text, get_summery(article_body_text)),
    ArticleSelectionInfo(),
    ArticleContextInfo(),
)
article.write()
print(article)
