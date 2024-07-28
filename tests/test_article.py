import pytest
from article_overload.db.models import ArticleRecord
from article_overload.db.objects import Article
from article_overload.db.utils import get_class_parameters

from .sample_data import (
    sample_article_records,
    sample_articles,
    sample_false_statements,
    sample_true_statements,
)


@pytest.mark.parametrize("article", sample_articles)
def test_get_parameters_returns_only_established_parameters(article: Article) -> None:
    result_parameters = get_class_parameters(article)
    expected_parameters = [
        "id",
        "url",
        "body_text",
        "summary",
        "questions",
        "incorrect_option_index",
        "title",
        "topic",
        "size",
        "author",
        "date_published",
    ]

    assert len(result_parameters) == len(expected_parameters)
    assert set(result_parameters) == set(expected_parameters)


@pytest.mark.parametrize(
    ("article", "article_record"),
    list(zip(sample_articles, sample_article_records, strict=True)),
)
def test_update_article_from_article_record(article: Article, article_record: ArticleRecord) -> None:
    article.update_id_from_article_record(article_record)

    assert article.id == article_record.id


@pytest.mark.parametrize(
    ("article", "true_statements"),
    list(zip(sample_articles, sample_true_statements, strict=True)),
)
def test_article_true_statements_returns_true_statements(
    article: Article,
    true_statements: list[str],
) -> None:
    assert article.true_statements == true_statements


@pytest.mark.parametrize(
    ("article", "false_statement"),
    list(zip(sample_articles, sample_false_statements, strict=True)),
)
def test_article_false_statements_returns_false_statements(
    article: Article,
    false_statement: list[str],
) -> None:
    assert article.false_statement == false_statement
