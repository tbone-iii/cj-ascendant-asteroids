import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from article_overload.db.handler import DatabaseHandler
from article_overload.db.objects import Article

JsonBody = list[dict[str, Any]]


def get_json_body(file_path: Path) -> JsonBody:
    """Get the JSON body.

    Description: This function does not need to be called outside of this module.
    It is important that we use the aboslute and full path to the file to avoid any issues with the file path.

    :return: The JSON body as a dictionary.
    """
    with file_path.open("r") as file:
        return json.load(file)


def load_articles(json_loaded_body: JsonBody) -> list[Article]:
    """Load articles from a JSON file to the `Article` pydantic model.

    Description: Pydantic is useful here to validate that the JSON body is exactly as expected, including the correct
    data types. This function does not need to be called outside of this module.

    :return: A list of `Article` objects.
    """
    article_dicts = json_loaded_body
    articles = []
    for article_dict in article_dicts:
        year, month, day = article_dict["date_published"].split("-")
        article_dict["date_published"] = datetime(
            year=int(year),
            month=int(month),
            day=int(day),
            tzinfo=UTC,
        )
        article = Article(**article_dict)
        articles.append(article)
    return articles


async def load_articles_to_database(json_path: Path, database_handler: DatabaseHandler) -> None:
    """Load articles to the database.

    Description: This function should be called outside of this module.
    It is an async call because the database itself is handled asynronously via the `DatabaseHandler` object.

    :param articles: A list of `Article` objects.
    :param database_handler: The database handler object.

    :return: None
    """
    json_body = get_json_body(json_path)
    articles = load_articles(json_body)
    await database_handler.add_articles(articles)


if __name__ == "__main__":
    json_file_name = "sample_articles.json"
    path = Path(__file__).resolve().parent / json_file_name

    data: Any = []
    with path.open("r") as file:
        data = json.load(file)

    article_dicts = data["articles"]
    for article_dict in article_dicts:
        article = Article(**article_dict)
        print(article)
        print()
