import html
import json
from pathlib import Path
from typing import Any


def clean_html_entities(json_data: Any) -> Any:  # noqa: ANN401
    """Recursively clean HTML entities in the JSON data."""
    if isinstance(json_data, dict):
        return {k: clean_html_entities(v) for k, v in json_data.items()}
    if isinstance(json_data, list):
        return [clean_html_entities(item) for item in json_data]
    if isinstance(json_data, str):
        return html.unescape(json_data)
    return json_data


def clean_json_file(input_file: str, output_file: str) -> None:
    """Load JSON file, clean HTML entities, and save the cleaned data."""
    with Path(input_file).open(encoding="utf-8") as f:
        data: list | dict = json.load(f)

    cleaned_data: Any = clean_html_entities(data)

    with Path(output_file).open("w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    input_file: str = "articles.json"
    output_file: str = "cleaned_articles.json"

    clean_json_file(input_file, output_file)
    print(f"Cleaned JSON file saved to {output_file}")
