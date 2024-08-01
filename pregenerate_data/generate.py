import json
import os
from datetime import UTC, datetime
from inspect import cleandoc
from pathlib import Path
from typing import Any

import openai
from dotenv import load_dotenv

from pregenerate_data.summarize import Article, ArticleContextInfo, ArticleSelectionInfo, ArticleTextInfo

load_dotenv()
GPT_MODEL = "gpt-4o"
openai.api_key = os.getenv("OPEN_AI_KEY")


def get_gpt_response(prompt_text: str) -> str:
    """Get a ChatGPT input and output."""
    response = openai.chat.completions.create(
        model=GPT_MODEL,
        messages=[
            {
                "role": "system",
                "content": prompt_text,
            },
        ],
    )

    return response.choices[0].message.content or ""


def get_summary(article_body: str) -> str:
    """Get a summary from body text."""
    prompt = cleandoc(
        """Please summarize the following article in around facts,
            each fact sentence should be no longer than 10 words,
            label ONLY 3 (THREE) of these sentences with <>, Ex: <This is a sentence>
            (Please don't include bullet points or numbers in the brackets)
            then add ONLY 1 (ONE) sentence containing fake information, wrapped in [This is a fake sentence] instead
            Please never but [] inside of <> or vise versa.
            Also ensure that there are line breaks between each sentence.

            For example, if the article is about a new type of car, you could say:

            <The car is red>
            <The car is fast>
            This is a statement
            <The car is expensive>
            [This is a false statement]

            ---
            Here is the article below:
            ---
    """
        + article_body,
    )
    return get_gpt_response(prompt)


def sanitize_text_via_gpt(body: str) -> str:
    """Rewrite the body text to remove any weird characters.

    Use ChatGPT for this.
    """
    return get_gpt_response(
        cleandoc(
            """Rewrite the following text to remove any weird characters,
            but keep as much as the original content as possible.
            Just remove anything that doesn't make sense or HTML content, or strange backslash characters like
            \\u:\n"""
            + body
        )
    )


def write_topic(  # noqa: PLR0913
    body: str,
    title: str,
    url: str,
    author: str,
    topic: str,
    date: datetime,
) -> bool:
    """Write a topic."""
    # Discord body embed length limit is 4096, but set to 3500
    max_length = 3500
    if len(body) > max_length:
        print(f"Body too long for {title=}, truncating")
        body = body[:3500] + "..."

    title = sanitize_text_via_gpt(title)
    body = sanitize_text_via_gpt(body)
    summary = get_summary(body)
    article = Article(
        ArticleTextInfo(body_text=body, summary=summary),
        ArticleSelectionInfo(topic=topic),
        ArticleContextInfo(title=title, url=url, author=author, date=date),
    )

    # Verify that the article has sentence options
    if article.article_text_info.sentence_options is None:
        print(f"Failed to write {title=} due to no sentence options.")
        return False

    # Verify that the article has a false sentence
    if article.article_text_info.incorrect_option is None:
        print(f"Failed to write {title=} due to no false sentence.")
        return False

    # Verify that there are not too many sentence options
    length = len(article.article_text_info.sentence_options)
    limits = (3, 5)
    if not (limits[0] <= length <= limits[1]):
        print(f"Failed to write {title=} due to too many or too few sentence options.")
        return False

    # Verify that the sentence options exist in the
    for question in article.article_text_info.sentence_options:
        if not question:
            print(f"Failed to write {title=} due an empty sentence.")
            return False
        if question not in summary:
            print(f"Failed to write {title=} due to a missing sentence within the summary.")
            return False

    article.write()
    print(f"Successfully wrote {title=}.")
    return True


def parse_json_article(json_article: dict[str, Any]) -> bool:
    """Parse a JSON article."""
    title = json_article["title"]
    url = json_article["url"]
    body = json_article["text"]
    author = json_article["author"]

    if "catgory" in json_article:
        topic = json_article["catgory"].title()
    elif "category" in json_article:
        topic = json_article["category"].title()
    else:
        topic = "Not Provided"

    parsed_date = datetime.strptime(json_article["publish_date"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC)

    return write_topic(
        body=body,
        title=title,
        url=url,
        author=author,
        topic=topic,
        date=parsed_date,
    )


def main(path: Path) -> None:
    """Run main generation."""
    with path.open(encoding="utf-8") as file:
        json_articles = json.load(file)

    articles_per_news_topic = [news["news"] for news in json_articles["top_news"]]
    article: dict[str, Any]
    for articles in articles_per_news_topic:
        for article in articles:
            result = parse_json_article(article)
            if result:
                break
            print(f"Failed to write {article['title']=}.")
