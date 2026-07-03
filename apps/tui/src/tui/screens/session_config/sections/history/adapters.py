from api_client.models import (
    FullHistoryConfigCreate,
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
    if isinstance(config, SlidingWindowHistoryConfigRead):
        return SlidingWindowHistoryFormState(window_size=str(config.window_size))

    return FullHistoryFormState()


# TODO: Why not use match case?
def history_create_from_form_state(state: HistoryFormState) -> HistoryConfigCreate:
    if isinstance(state, SlidingWindowHistoryFormState):
        try:
            window_size = int(state.window_size)
        except ValueError as exc:
            raise SessionConfigValidationError("History window size must be a whole number") from exc

        return SlidingWindowHistoryConfigCreate(
            window_size=max(1, window_size),
        )

    return FullHistoryConfigCreate()
