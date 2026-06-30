from collections.abc import Callable
from typing import TypeVar

from textual.message import Message

StateT = TypeVar("StateT")

type StateUpdate[StateT] = Callable[[StateT], StateT]


class StateChanged[StateT](Message):
    def __init__(self, update: StateUpdate[StateT]) -> None:
        super().__init__()
        self.update = update
