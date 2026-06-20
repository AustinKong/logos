from typing import Protocol


class StreamableWidget(Protocol):
    def append_content(self, content: str) -> None: ...

    # This function needs to exist for non-streaming (initial population)
    def set_content(self, content: str) -> None: ...
