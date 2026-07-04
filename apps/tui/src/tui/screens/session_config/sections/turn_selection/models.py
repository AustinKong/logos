from api_client.models import TurnSelectionMode
from attrs import define


@define(frozen=True)
class RoundRobinTurnSelectionFormState:
    mode: TurnSelectionMode = TurnSelectionMode.ROUND_ROBIN


@define(frozen=True)
class ShuffledTurnSelectionFormState:
    mode: TurnSelectionMode = TurnSelectionMode.SHUFFLED


type TurnSelectionFormState = RoundRobinTurnSelectionFormState | ShuffledTurnSelectionFormState
