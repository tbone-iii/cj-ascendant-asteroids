from article_overload.db.items.article_handler import ArticleHandler

from .sample_data import sample_articles


def test_article_handler_marked_up_summary_has_all_sentences() -> None:
    article = sample_articles[0]
    article_handler = ArticleHandler(article)
    marked_up_summary = article_handler.marked_up_summary

    for sentence in article.true_statements:
        assert sentence in marked_up_summary
    assert article.false_statement in marked_up_summary


def test_article_handler_highlight_answer_in_summary_has_all_sentences() -> None:
    article = sample_articles[0]
    article_handler = ArticleHandler(article)
    highlight_answer_in_summary = article_handler.highlighted_summary

    for sentence in article.true_statements:
        assert sentence in highlight_answer_in_summary
    assert article.false_statement in highlight_answer_in_summary
