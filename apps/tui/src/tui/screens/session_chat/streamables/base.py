from typing import Protocol


class StreamableWidget(Protocol):
    def append_content(self, content: str) -> None: ...

    # This function needs to exist for non-streaming
    def set_content(self, content: str) -> None: ...
