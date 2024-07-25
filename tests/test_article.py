import pytest
from article_overload.db.models import ArticleRecord
from article_overload.db.objects import Article
from article_overload.db.utils import get_class_parameters

from .sample_data import sample_article_records, sample_articles


@pytest.mark.parametrize("article", sample_articles)
def test_get_parameters_returns_only_established_parameters(article: Article) -> None:
    result_parameters = get_class_parameters(article)
    expected_parameters = ["id", "url", "body_text", "summary"]

    assert len(result_parameters) == len(expected_parameters)
    assert set(result_parameters) == set(expected_parameters)


@pytest.mark.parametrize("article", sample_articles)
def test_create_article_record_creates_article_record_from_article(article: Article) -> None:
    article_record = article.create_article_record()

    assert hasattr(article_record, "id")


@pytest.mark.parametrize(
    ("article", "article_record"),
    list(zip(sample_articles, sample_article_records, strict=True)),
)
def test_update_article_from_article_record(article: Article, article_record: ArticleRecord) -> None:
    article.update_id_from_article_record(article_record)

    assert article.id == article_record.id
