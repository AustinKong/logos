from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

from textual import on as textual_on
from textual.message import Message

P = ParamSpec("P")
R = TypeVar("R")


def on(
    message_type: type[Message],
    selector: str | None = None,
    *,
    stop: bool = True,
    **kwargs: str,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorate(method: Callable[P, R]) -> Callable[P, R]:
        @wraps(method)
        def wrapped(*args: P.args, **wrapped_kwargs: P.kwargs) -> R:
            event = args[1] if len(args) > 1 else None
            if stop and isinstance(event, Message):
                event.stop()
            return method(*args, **wrapped_kwargs)

        return textual_on(message_type, selector, **kwargs)(wrapped)

    return decorate
