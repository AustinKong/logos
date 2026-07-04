from typing import assert_never

from api_client.models import (
    FullHistoryConfigCreate,
    FullHistoryConfigRead,
    HistoryConfigCreate,
    HistoryConfigRead,
    SlidingWindowHistoryConfigCreate,
    SlidingWindowHistoryConfigRead,
)

from tui.screens.session_config.errors import SessionConfigValidationError
from tui.screens.session_config.sections.history.state import (
    FullHistoryFormState,
    HistoryFormState,
    SlidingWindowHistoryFormState,
)


def history_form_state_from_read(config: HistoryConfigRead) -> HistoryFormState:
    match config:
        case SlidingWindowHistoryConfigRead():
            return SlidingWindowHistoryFormState(window_size=str(config.window_size))
        case FullHistoryConfigRead():
            return FullHistoryFormState()
        case _ as never:
            assert_never(never)


def history_create_from_form_state(state: HistoryFormState) -> HistoryConfigCreate:
    match state:
        case SlidingWindowHistoryFormState():
            try:
                window_size = int(state.window_size)
            except ValueError as exc:
                raise SessionConfigValidationError("History window size must be a whole number") from exc

            return SlidingWindowHistoryConfigCreate(
                window_size=max(1, window_size),
            )
        case FullHistoryFormState():
            return FullHistoryConfigCreate()
        case _ as never:
            assert_never(never)
