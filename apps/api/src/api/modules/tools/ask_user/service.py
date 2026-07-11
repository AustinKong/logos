from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session as SqlAlchemyDb

from api.modules.ai.service import AIService
from api.modules.sessions.models.events import Event
from api.modules.sessions.service import SessionService
from api.modules.tools.ask_user.cache import AskUserCacheRepository
from api.modules.tools.ask_user.errors import (
    AskUserAlreadyAnsweredError,
    AskUserStartedEventNotFoundError,
    InvalidAskUserAnswerError,
)
from api.modules.tools.ask_user.models import (
    AskUserAnswerKind,
    AskUserCacheEntryData,
    AskUserCompletedEvent,
    AskUserStartedEvent,
)

ASK_USER_CACHE_MAX_DISTANCE = 0.25


class AskUserService:
    def __init__(
        self,
        *,
        db: SqlAlchemyDb,
        session_service: SessionService,
        ai_service: AIService,
        cache_repository: AskUserCacheRepository,
    ) -> None:
        self._db = db
        self._session_service = session_service
        self._ai_service = ai_service
        self._cache_repository = cache_repository

    async def start(
        self,
        *,
        session_id: UUID,
        question: str,
        options: list[str],
    ) -> list[Event]:
        ask_user_id = uuid4()
        if cached_completed_event := await self._find_cached_completed_event(session_id=session_id, question=question):
            cache_entry_id, completed_event = cached_completed_event
            return [
                AskUserStartedEvent(
                    session_id=session_id,
                    ask_user_id=ask_user_id,
                    question=question,
                    options=options,
                    cache_entry_id=cache_entry_id,
                ),
                AskUserCompletedEvent(
                    session_id=session_id,
                    ask_user_id=ask_user_id,
                    answer_kind=completed_event.answer_kind,
                    answer=completed_event.answer,
                ),
            ]

        return [
            AskUserStartedEvent(
                session_id=session_id,
                ask_user_id=ask_user_id,
                question=question,
                options=options,
                cache_entry_id=None,
            )
        ]

    async def answer(
        self,
        *,
        session_id: UUID,
        ask_user_id: UUID,
        answer_kind: AskUserAnswerKind,
        answer: str,
    ) -> AskUserCompletedEvent:
        self._session_service.get_session(session_id)
        started_event = self._get_started_event(session_id=session_id, ask_user_id=ask_user_id)
        ended_event = self._get_ended_event(session_id=session_id, ask_user_id=ask_user_id)

        if ended_event is not None:
            raise AskUserAlreadyAnsweredError()

        if answer_kind is AskUserAnswerKind.OPTION and answer not in started_event.options:
            raise InvalidAskUserAnswerError("Answer must match one of the provided options")
        elif answer_kind is AskUserAnswerKind.FREE_TEXT and not answer:
            raise InvalidAskUserAnswerError("Free-text answer must not be empty")

        completed_event = AskUserCompletedEvent(
            session_id=session_id,
            ask_user_id=ask_user_id,
            answer_kind=answer_kind,
            answer=answer,
        )
        self._db.add(completed_event)
        self._db.commit()
        await self._cache_answer(started_event=started_event, completed_event=completed_event)
        return completed_event

    async def _find_cached_completed_event(
        self,
        *,
        session_id: UUID,
        question: str,
    ) -> tuple[UUID, AskUserCompletedEvent] | None:
        # If cache lookup fails, treat as a cache miss.
        try:
            vector = await self._ai_service.embed(text=question)
            cache_entry = await self._cache_repository.find_nearest(
                session_id=session_id,
                vector=vector,
                max_distance=ASK_USER_CACHE_MAX_DISTANCE,
            )
            if cache_entry is None:
                return None

            completed_event = self._db.get(AskUserCompletedEvent, cache_entry.source_completed_event_id)
            if completed_event is None:
                return None

            return cache_entry.id, completed_event
        except:
            pass

    def _get_started_event(self, *, session_id: UUID, ask_user_id: UUID) -> AskUserStartedEvent:
        statement = (
            select(AskUserStartedEvent)
            .where(AskUserStartedEvent.session_id == session_id)
            .where(AskUserStartedEvent.ask_user_id == ask_user_id)
        )
        started_event = self._db.execute(statement).scalar_one_or_none()
        if started_event is None:
            raise AskUserStartedEventNotFoundError()
        return started_event

    def _get_ended_event(self, *, session_id: UUID, ask_user_id: UUID) -> AskUserCompletedEvent | None:
        statement = (
            select(AskUserCompletedEvent)
            .where(AskUserCompletedEvent.session_id == session_id)
            .where(AskUserCompletedEvent.ask_user_id == ask_user_id)
        )
        return self._db.execute(statement).scalar_one_or_none()

    async def _cache_answer(
        self,
        *,
        started_event: AskUserStartedEvent,
        completed_event: AskUserCompletedEvent,
    ) -> None:
        # If caching fails, silently ignore the error since its non-critical.
        try:
            vector = await self._ai_service.embed(text=started_event.question)
            await self._cache_repository.add_entry(
                AskUserCacheEntryData(
                    session_id=started_event.session_id,
                    vector=vector,
                    source_completed_event_id=completed_event.id,
                )
            )
        except:
            pass
