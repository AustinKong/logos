from api_client.models import HistoryMode
from attrs import define


@define(frozen=True)
class FullHistoryFormState:
    mode: HistoryMode = HistoryMode.FULL


@define(frozen=True)
class SlidingWindowHistoryFormState:
    window_size: str
    mode: HistoryMode = HistoryMode.SLIDING_WINDOW


type HistoryFormState = FullHistoryFormState | SlidingWindowHistoryFormState
