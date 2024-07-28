import asyncio
from collections.abc import Sequence
from typing import TypeVar

from sqlalchemy import Float, Subquery, and_, case, cast, select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from sqlalchemy.sql.expression import func, true

from article_overload.db.items.article_handler import ArticleHandler
from article_overload.exceptions import (
    NoArticlesFoundError,
    NoSessionFoundError,
    SizeRecordNotFoundError,
)

from .models import (
    ArticleRecord,
    ArticleResponseRecord,
    QuestionRecord,
    SessionRecord,
    SizeRecord,
    init_database,
)
from .objects import (
    Article,
    ArticleResponse,
    Score,
    UserTopicStat,
)

T = TypeVar("T")


class DatabaseHandler:
    """Asynchronous database handler class.

    Session management is handled by the `with_session` decorator.
    """

    def __init__(self, database_url: str) -> None:
        self.database_url = database_url
        self.engine: AsyncEngine
        self.session_factory: async_sessionmaker[AsyncSession]

    @classmethod
    async def create(cls, database_url: str) -> "DatabaseHandler":
        """Create a new instance of the DatabaseHandler.

        :Return: `DatabaseHandler`
        """
        self = cls(database_url)
        self.engine = await init_database(database_url)
        self.session_factory = async_sessionmaker(self.engine, expire_on_commit=False)
        return self

    async def get_size_record_by_size(self, size: str, session: AsyncSession) -> SizeRecord:
        """Get size record by size.

        If it doesn't exist, create a new entry to the database and return it.

        :Return: `SizeRecord` or `None`
        """
        result = await session.execute(select(SizeRecord).where(SizeRecord.size == size))
        size_record = result.scalars().first()

        if size_record is None:
            size_record = SizeRecord(size=size)
            session.add(size_record)
            await session.flush()
        return size_record

    async def add_article(self, article: Article) -> Article:
        """Add `Article` to database. Return the updated `Article`.

        :Return: `Article`
        """
        # parse down Article summary and fake_fact

        async with self.session_factory() as session:
            async with session.begin():
                size_record = await self.get_size_record_by_size(article.size, session)
                article_record = article.create_article_record(size_record)
                session.add(article_record)

            return article.update_id_from_article_record(article_record)

    async def add_articles(self, articles: list[Article]) -> list[Article]:
        """Add multiple articles to the database. Return the new Articles.

        This is a bulk insert operation.
        :Return: `list[Article]`
        """
        async with self.session_factory() as session:
            async with session.begin():
                size_records = [await self.get_size_record_by_size(article.size, session) for article in articles]
                article_records = [
                    article.create_article_record(size_record)
                    for article, size_record in zip(articles, size_records, strict=False)
                ]
                session.add_all(article_records)

            return [
                article.update_id_from_article_record(article_record)
                for article, article_record in zip(articles, article_records, strict=False)
            ]

    async def get_article_by_id(self, article_id: int) -> Article | None:
        """Get `Article` by ID.

        :Return: `Article` or `None`
        """
        async with self.session_factory() as session:
            article_record = await session.get(ArticleRecord, article_id)

            if article_record is None:
                return None

            question_records = await self.get_question_records_from_article_record(article_record, session)
            size_record = await self.get_size_records_from_article_record(article_record, session)

            return Article.create_from_article_record(
                article_record=article_record,
                question_records=list(question_records),
                size_record=size_record,
            )

    @staticmethod
    async def get_question_records_from_article_record(
        article_record: ArticleRecord,
        session: AsyncSession,
    ) -> Sequence[QuestionRecord]:
        """Get question record from article record.

        :Return: `list[QuestionRecord]`
        """
        result = await session.execute(article_record.questions.select())
        return result.scalars().all()

    @staticmethod
    async def get_size_records_from_article_record(article_record: ArticleRecord, session: AsyncSession) -> SizeRecord:
        """Get size record from article records.

        :Return: `SizeRecord` or `None`
        """
        size_record = await session.get(SizeRecord, article_record.size_id)
        if size_record is None:
            raise SizeRecordNotFoundError

        return size_record

    async def get_all_articles(self) -> list[Article]:
        """Get all articles.

        :See:
        https://docs.sqlalchemy.org/en/20/core/connections.html#sqlalchemy.engine.Row

        :Return: `list[Article]`
        """
        async with self.session_factory() as session:
            result = await session.execute(select(ArticleRecord))
            article_records = result.scalars().all()
            questions_records = [
                await self.get_question_records_from_article_record(article_record, session)
                for article_record in article_records
            ]
            size_records = [
                await self.get_size_records_from_article_record(article_record, session)
                for article_record in article_records
            ]

            return [
                Article.create_from_article_record(
                    article_record=article_record,
                    question_records=list(question_records),
                    size_record=size_record,
                )
                for article_record, question_records, size_record in zip(
                    article_records,
                    questions_records,
                    size_records,
                    strict=True,
                )
            ]

    async def get_random_article(self) -> ArticleHandler:
        """Get a random article.

        :Return: `Article`
        """
        async with self.session_factory() as session:
            result = await session.execute(select(ArticleRecord).order_by(func.random()).limit(1))
            article_record = result.scalars().first()

            if article_record is None:
                raise NoArticlesFoundError

            question_records = await self.get_question_records_from_article_record(article_record, session)
            size_record = await self.get_size_records_from_article_record(article_record, session)

            article = Article.create_from_article_record(
                article_record=article_record,
                question_records=list(question_records),
                size_record=size_record,
            )
            return ArticleHandler(article)

    async def get_global_ratio_correct_on_article(self, article: Article) -> float | None:
        """Get the global ratio correct on an article.

        If the article has never been answered before, return None.

        :Return: `float` | None
        """
        async with self.session_factory() as session:
            result = await session.execute(
                select(func.count())
                .select_from(ArticleResponseRecord)
                .where(ArticleResponseRecord.article_id == article.id),
            )
            total_responses = result.scalar()

            if total_responses == 0 or total_responses is None:
                return None

            result = await session.execute(
                select(func.count())
                .select_from(ArticleResponseRecord)
                .where(
                    and_(
                        ArticleResponseRecord.article_id == article.id,
                        ArticleResponseRecord.correct == true(),
                    ),
                ),
            )
            total_correct = result.scalar()

            if total_correct is None:
                total_correct = 0

            return total_correct / total_responses

    async def add_article_response_from_article(
        self,
        article: Article,
        article_response: ArticleResponse,
    ) -> ArticleResponseRecord:
        """Add an article response to the database with the given parameters.

        Args:
        ----
            article (Article): The article object for which the response is being added.
            article_response (ArticleResponse): The article response object containing the response details.

        Raises:
        ------
            NoArticlesFoundError: If the article record is not found in the database.

        Returns:
        -------
            ArticleResponseRecord: The newly created article response record.

        Note:
        ----
            This method is not meant to be used by the client-facing application.

        """
        async with self.session_factory() as session:
            async with session.begin():
                article_record = await session.get(ArticleRecord, article.id)
                if article_record is None:
                    raise NoArticlesFoundError

                article_response_record = ArticleResponseRecord(
                    user_id=article_response.user_id,
                    session_id=article_response.session_id,
                    response=article_response.response,
                    correct=article_response.is_correct,
                    answered_on=func.now(),
                )
                article_record.article_responses.add(article_response_record)

            return article_response_record

    async def start_new_session(self, user_id: int) -> SessionRecord:
        """Start a new session for a user.

        :Return: `None`
        """
        async with self.session_factory() as session:
            async with session.begin():
                session_record = SessionRecord(
                    user_id=user_id,
                    start_date=func.now(),
                    end_date=func.now(),
                    score=0,
                )
                session.add(session_record)

            return session_record

    async def start_new_sessions(self, user_ids: list[int]) -> list[SessionRecord]:
        """Start multiple sessions at once asynchronously.

        :Return: `list[SessionRecord]`
        """
        coros = [self.start_new_session(user_id) for user_id in user_ids]
        return await asyncio.gather(*coros)

    async def end_session(self, session_id: int, score: int) -> SessionRecord:
        """End a session for a user based on the session id.

        The client should not be using the return statement.

        :Return: `SessionRecord`
        """
        async with self.session_factory() as session:
            async with session.begin():
                session_record = await session.get(SessionRecord, session_id)

                if session_record is None:
                    raise NoSessionFoundError

                session_record.score = score
                session_record.end_date = func.now()

            return session_record

    async def end_sessions(self, session_ids: list[int], scores: list[int]) -> list[SessionRecord]:
        """End multiple sessions at once asynchronously.

        :Return: `list[SessionRecord]`
        """
        coros = [
            self.end_session(session_id=session_id, score=score)
            for session_id, score in zip(session_ids, scores, strict=True)
        ]
        return await asyncio.gather(*coros)

    async def get_player_score(self, user_id: int) -> Score:
        """Get the player's score based on the user ID.

        :Return: `Score`
        """
        async with self.session_factory() as session:
            result = await session.execute(
                select(
                    func.sum(SessionRecord.score).label("total_score"),
                    func.max(SessionRecord.end_date).label("most_recent_played"),
                ).where(SessionRecord.user_id == user_id),
            )
            record = result.fetchone()
            if record is None:
                return Score(user_id=user_id, score=0, latest_played=None)

            return Score(
                user_id=user_id,
                score=record.total_score or 0,
                latest_played=record.most_recent_played,
            )

    async def get_top_n_scores(self, n: int) -> list[Score]:
        """Get the top N scores.

        :Return: `list[Score]`
        """
        async with self.session_factory() as session:
            subquery = (
                select(
                    SessionRecord.user_id,
                    func.sum(SessionRecord.score).label("score"),
                    func.max(SessionRecord.end_date).label("latest_played"),
                )
                .group_by(SessionRecord.user_id)
                .order_by(
                    func.sum(SessionRecord.score).desc(),
                    func.max(SessionRecord.end_date).desc(),
                )
                .limit(n)
            )
            result = await session.execute(subquery)
            query_results = result.mappings()

            return [
                Score(
                    user_id=query_result.user_id,
                    score=query_result.score,
                    latest_played=query_result.latest_played,
                )
                for query_result in query_results
            ]

    async def get_player_topic_stat(self, user_id: int, topic: str | None = None) -> UserTopicStat:
        """Get the player's topic stats for a specific topic or ALL topics if None is passed.

        :Return: `TopicStat`
        """
        count_subquery = self._get_count_query_for_user_grouped_by_topic(user_id)
        correct_count_subquery = self._get_correct_count_query_for_user_grouped_by_topic(user_id)

        # None topic means to look at ALL topics
        if topic is None:
            # Look at all topics and sum them up across the user ID by querying count query
            count_query = select(func.sum(count_subquery.columns.total_responses).label("total_responses"))
            correct_count_query = select(func.sum(correct_count_subquery.columns.total_correct).label("total_correct"))
        else:
            count_query = select(count_subquery.columns.total_responses).where(count_subquery.columns.topic == topic)
            correct_count_query = select(correct_count_subquery.columns.total_correct).where(
                correct_count_subquery.columns.topic == topic,
            )

        async with self.session_factory() as session:
            total_responses_result = await session.execute(count_query)
            correct_count_result = await session.execute(correct_count_query)

            total_responses = total_responses_result.scalar() or 0
            total_correct = correct_count_result.scalar() or 0

            return UserTopicStat(
                user_id=user_id,
                total_correct=total_correct,
                total_responses=total_responses,
                topic=topic,
            )

    async def get_player_topic_stats_in_order(self, user_id: int) -> list[UserTopicStat]:
        """Get the player's topic stats for all topics, ranked by correctness ratio.

        If the correctness ratios match, the topics should be ordered by the number of responses.
        """
        count_subquery = self._get_count_query_for_user_grouped_by_topic(user_id)
        correct_count_subquery = self._get_correct_count_query_for_user_grouped_by_topic(user_id)

        ratio_correct = case(
            (
                count_subquery.columns.total_responses != 0,
                cast(correct_count_subquery.columns.total_correct, Float) / count_subquery.columns.total_responses,
            ),
            else_=0,
        ).label("ratio_correct")

        result_query = (
            select(
                count_subquery.columns.user_id,
                count_subquery.columns.topic,
                count_subquery.columns.total_responses,
                ratio_correct,
                correct_count_subquery.columns.total_correct,
            )
            .select_from(count_subquery)
            .outerjoin(
                correct_count_subquery,
                onclause=and_(
                    count_subquery.columns.user_id == correct_count_subquery.columns.user_id,
                    count_subquery.columns.topic == correct_count_subquery.columns.topic,
                ),
            )
            .order_by(
                ratio_correct.desc(),
                count_subquery.columns.total_responses.desc(),
            )
        )
        async with self.session_factory() as session:
            result = await session.execute(result_query)
            return [
                UserTopicStat(
                    topic=query_result.topic,
                    total_correct=(query_result.total_correct if query_result.total_correct is not None else 0),
                    total_responses=query_result.total_responses,
                    user_id=query_result.user_id,
                )
                for query_result in result.mappings()
            ]

    def _get_count_query_for_user_grouped_by_topic(self, user_id: int) -> Subquery:
        """Get the count query for a user.

        Equivalent to a SQL group by on the user ID and topic.

        :Return: `select`
        """
        return (
            select(
                ArticleResponseRecord.user_id,
                ArticleRecord.topic,
                func.count().label("total_responses"),
            )
            .join(ArticleResponseRecord)
            .join(SessionRecord)
            .where(ArticleResponseRecord.user_id == user_id)
            .group_by(ArticleRecord.topic, ArticleResponseRecord.user_id)
        ).subquery()

    def _get_correct_count_query_for_user_grouped_by_topic(self, user_id: int) -> Subquery:
        """Get the correct count query for a user.

        Equivalent to a SQL group by on the user ID and topic.

        :Return: `select`
        """
        return (
            select(
                ArticleResponseRecord.user_id,
                ArticleRecord.topic,
                func.count().label("total_correct"),
            )
            .join(ArticleResponseRecord)
            .join(SessionRecord)
            .where(
                and_(
                    ArticleResponseRecord.user_id == user_id,
                    ArticleResponseRecord.correct == true(),
                ),
            )
            .group_by(ArticleRecord.topic, ArticleResponseRecord.user_id)
        ).subquery()
