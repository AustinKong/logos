from uuid import UUID

from sqlalchemy.orm import Session as SqlAlchemyDb

from api.modules.ai.service import AIService
from api.modules.sessions.models.events import AskUserCompletedEvent, AskUserStartedEvent, Event
from api.modules.tools.ask_user.cache import AskUserCacheRepository
from api.modules.tools.ask_user.errors import (
    AskUserAlreadyAnsweredError,
    AskUserStartedEventNotFoundError,
    InvalidAskUserAnswerError,
)
from api.modules.tools.ask_user.models import AskUserAnswerKind, AskUserCacheEntryData

ASK_USER_CACHE_MAX_DISTANCE = 0.25


class AskUserService:
    def __init__(
        self,
        *,
        db: SqlAlchemyDb,
        ai_service: AIService,
        cache_repository: AskUserCacheRepository,
    ) -> None:
        self._db = db
        self._ai_service = ai_service
        self._cache_repository = cache_repository

    async def start(
        self,
        *,
        session_id: UUID,
        question: str,
        options: list[str],
    ) -> list[Event]:
        started_event = AskUserStartedEvent(
            session_id=session_id,
            question=question,
            options=options,
            cache_entry_id=None,
        )
        if cached_completed_event := await self._find_cached_completed_event(session_id=session_id, question=question):
            cache_entry_id, completed_event = cached_completed_event
            started_event.cache_entry_id = cache_entry_id
            return [
                started_event,
                AskUserCompletedEvent(
                    session_id=session_id,
                    started_event=started_event,
                    answer_kind=completed_event.answer_kind,
                    answer=completed_event.answer,
                ),
            ]

        return [started_event]

    async def answer(
        self,
        *,
        started_event_id: UUID,
        answer_kind: AskUserAnswerKind,
        answer: str,
    ) -> AskUserCompletedEvent:
        started_event = self._get_started_event(started_event_id=started_event_id)

        if started_event.completed_event is not None:
            raise AskUserAlreadyAnsweredError()

        if answer_kind is AskUserAnswerKind.OPTION and answer not in started_event.options:
            raise InvalidAskUserAnswerError("Answer must match one of the provided options")
        elif answer_kind is AskUserAnswerKind.FREE_TEXT and not answer:
            raise InvalidAskUserAnswerError("Free-text answer must not be empty")

        completed_event = AskUserCompletedEvent(
            session_id=started_event.session_id,
            started_event=started_event,
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

    def _get_started_event(self, *, started_event_id: UUID) -> AskUserStartedEvent:
        started_event = self._db.get(AskUserStartedEvent, started_event_id)
        if started_event is None:
            raise AskUserStartedEventNotFoundError()
        return started_event

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
