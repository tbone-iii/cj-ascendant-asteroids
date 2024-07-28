from random import shuffle

from article_overload.db.items.sentence import Sentence
from article_overload.db.items.sentence_type import SentenceType
from article_overload.db.objects import Article

ActiveSentenceTypes = (SentenceType.TRUE, SentenceType.FALSE)


class ArticleHandler:
    """A class to handle the `Article` data object.

    This can handle the `Article` data object and provide methods to manipulate the data, as well as
    store the marked up version of the summary text, store the sentence randomization, and so on.
    """

    def __init__(self, article: Article) -> None:
        self._article = article
        self.sentences = parse_sentences(article.summary)
        shuffle(self.sentences)  # to randomize sentence order

        # Calculated attributes
        self.active_sentences: list[Sentence] = get_active_sentences(self.sentences)
        self.false_sentence: Sentence = get_false_sentence(self.active_sentences)

        # Relevant article attributes
        self._raw_summary = article.summary
        self.url = article.url
        self.body_text = article.body_text
        self.title = article.title
        self.topic = article.topic
        self.size = article.size
        self.author = article.author
        self.date_published = article.date_published

    @property
    def raw_text_active_sentences(self) -> list[str]:
        """Return the raw text of the active sentences.

        :Return: `str`
        """
        return [sentence.text for sentence in self.active_sentences]

    @property
    def marked_up_summary(self) -> str:
        """Return the summary text with the sentence options bolded.

        :Return: `str`
        """
        counter = 1
        formatted_hidden_sentences = []
        for sentence in self.sentences:
            if sentence.sentence_type not in ActiveSentenceTypes:
                formatted_hidden_sentences.append(sentence.formatted_sentence_hidden(None))
                continue

            formatted_hidden_sentences.append(sentence.formatted_sentence_hidden(counter))
            counter += 1
        return " ".join(formatted_hidden_sentences)

    @property
    def highlighted_summary(self) -> str:
        """Return the summary text with the false statement bolded with the other statements striked out.

        :Return: `str`
        """
        counter = 1
        formatted_hidden_sentences = []
        for sentence in self.sentences:
            if sentence.sentence_type not in ActiveSentenceTypes:
                formatted_hidden_sentences.append(sentence.formatted_sentence_result(None))
                continue

            formatted_hidden_sentences.append(sentence.formatted_sentence_result(counter))
            counter += 1
        return " ".join(formatted_hidden_sentences)


def build_sentence_from_string(sentence: str) -> Sentence:
    """Build a `Sentence` object from a string.

    :Return: `Sentence`
    """
    if sentence.startswith("[") and sentence.endswith("]"):
        cleaned_sentence = sentence.removeprefix("[").removesuffix("]")
        return Sentence(cleaned_sentence, sentence_type=SentenceType.FALSE)

    if sentence.startswith("<") and sentence.endswith(">"):
        cleaned_sentence = sentence.removeprefix("<").removesuffix(">")
        return Sentence(cleaned_sentence, sentence_type=SentenceType.TRUE)

    if sentence.startswith('"') and sentence.endswith('"'):
        cleaned_sentence = sentence.removeprefix('"').removesuffix('"')
        return Sentence(cleaned_sentence, sentence_type=SentenceType.NEUTRAL)

    # TODO: This should never be reached, but workaround is to return a neutral sentence
    return Sentence(sentence, sentence_type=SentenceType.NEUTRAL)

    raise ValueError


def parse_sentences(summary: str) -> list[Sentence]:
    """Parse the summary text into a list of sentences.

    Structure assumption:
    - Summary text is separated by newlines.
    - Each sentence wrapped in [] will be considered a true statement.
    - Each sentence wrapped in <> will be considered a false statement.

    :Return: `list[str]`
    """
    original_sentences = summary.splitlines()
    stripped_sentences = (sentence.strip() for sentence in original_sentences if sentence.strip())
    return [build_sentence_from_string(sentence) for sentence in stripped_sentences]


def get_active_sentences(sentences: list[Sentence]) -> list[Sentence]:
    """Return the active sentences.

    :Return: `list[Sentence]`
    """
    return [sentence for sentence in sentences if sentence.sentence_type in ActiveSentenceTypes]


def get_false_sentence(sentences: list[Sentence]) -> Sentence:
    """Return the false statement.

    :Return: `Sentence`
    """
    try:
        return next(sentence for sentence in sentences if sentence.sentence_type == SentenceType.FALSE)
    except StopIteration:
        return Sentence("<No false statement found.>", sentence_type=SentenceType.FALSE)
