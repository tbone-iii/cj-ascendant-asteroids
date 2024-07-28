import json
import os
from datetime import UTC, datetime
from pathlib import Path

import openai
from dotenv import load_dotenv
from summarize import Article, ArticleContextInfo, ArticleSelectionInfo, ArticleTextInfo

load_dotenv()
GPT_MODEL = "gpt-4o"
openai.api_key = os.getenv("OPEN_AI_KEY")


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
            label 3 of these sentences with <>, Ex: <This is a sentence> \
            (Please don't include bullet points or numbers in the brackets) \
            then add a sentence containing fake information, wrapped in [] instead\n \
            Please never but [] inside of <> or vise versa\n \
    "
        + article_body,
    )


def write_topic(  # noqa: PLR0913
    body: str,
    title: str,
    url: str,
    author: list[str],
    topic: str,
    date: datetime,
) -> None:
    """Write a topic."""
    article = Article(
        ArticleTextInfo(
            body_text=body,
            summary=get_summary(body),
        ),
        ArticleSelectionInfo(topic=topic),
        ArticleContextInfo(title=title, url=url, author=author, date=date),
    )
    for question in article.article_text_info.sentence_options:
        if not question:
            return
    article.write()
    print(article)


with Path("./pregenerate_data/20240621_real_articles.json").open(encoding="utf-8") as file:
    json_articles = json.load(file)


bodies = [news["news"] for news in json_articles["top_news"]]
bodies = [news[0] for news in bodies]
for json_article in bodies:
    title = json_article["title"]
    url = json_article["url"]
    body = json_article["text"]
    author = json_article["author"]
    try:
        topic = json_article["catgory"].title()
    except Exception:  # noqa: BLE001
        topic = "General"

    date = parsed_date = datetime.strptime(json_article["publish_date"], "%Y-%m-%d %H:%M:%S", tzinfo=UTC)  # noqa: DTZ007

    write_topic(
        body=body,
        title=title,
        url=url,
        author=author,
        topic=topic,
        date=date,
    )
