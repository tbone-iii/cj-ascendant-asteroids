"""When you run this script, it will generate/update a database full of data referenced in a JSON file.

Certain tables are unaffected by the data in the JSON file, such as the `user` table.
This table is populated with a Discord user ID and their corresponding score, plus whatever other metadata
is meant to be tracked.
"""

import asyncio
from pathlib import Path

from article_overload.db.handler import DatabaseHandler
from article_overload.db.models import TableName
from pregenerate_data.load_articles import load_articles_to_database
from sqlalchemy import create_engine, text


def main() -> None:
    """Generate the database with the data from the JSON file.

    If the Article table exists, it will overwrite.
    """
    json_file_name = "./pregenerate_data/sample_articles.json"
    path = Path(__file__).resolve().parent / json_file_name
    database_relative_path = "pregenerate_data/article_overload.db"
    database_url = f"sqlite+aiosqlite:///{database_relative_path}"

    # The underlying schema of the table may have changed, thus drop and renew
    sync_engine = create_engine(database_url.replace("aiosqlite", "pysqlite"))
    with sync_engine.connect() as connection:
        statement = f"DROP TABLE IF EXISTS {TableName.ARTICLE.value}"
        connection.execute(text(statement))

    database_handler = asyncio.run(DatabaseHandler.create(database_url))
    asyncio.run(load_articles_to_database(path, database_handler=database_handler))


if __name__ == "__main__":
    main()
