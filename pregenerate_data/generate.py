import sys

import openai
from summarize import Article, ArticleTextInfo

GPT_MODEL = "gpt-4"
openai.api_key = sys.argv[1]


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


def write_topic(topic_words: str) -> None:
    """Write a topic."""
    article_body_text = get_gpt_response(topic_words)
    article = Article(ArticleTextInfo(article_body_text, get_summary(article_body_text)))
    article.write()
    print(article)


write_topic("Generate an article based on cats that is under 300 words")
write_topic("Generate an article based on dogs that is under 300 words")
write_topic("Generate an article based on boats that is under 300 words")
write_topic("Generate an article based on cars that is under 300 words")
write_topic("Generate an article based on planes that is under 300 words")
write_topic("Generate an article based on frogs that is under 300 words")
write_topic("Generate an article based on discord that is under 300 words")
write_topic("Generate an article based on the internet that is under 300 words")
write_topic("Generate an article based on robotics that is under 300 words")
write_topic("Generate an article based on garfield that is under 300 words")
