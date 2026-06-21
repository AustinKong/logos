from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from api_client import Client
from textual.app import App
from textual.message import Message

from tui.screens.session_config.screen import SessionConfigMode


class Route(StrEnum):
    SESSIONS = "sessions"
    SESSION_CONFIG = "session_config"
    SESSION_CHAT = "session_chat"


@dataclass(frozen=True, slots=True)
class SessionChatParams:
    session_id: UUID


@dataclass(frozen=True, slots=True)
class SessionConfigParams:
    mode: SessionConfigMode


class Navigate(Message):
    def __init__(self, route: Route, params: object | None = None) -> None:
        super().__init__()
        self.route = route
        self.params = params


class Navigator:
    def __init__(self, *, app: App[None], client: Client) -> None:
        self._app = app
        self._client = client

    def navigate(self, route: Route, params: object | None = None) -> None:
        match route:
            case Route.SESSIONS:
                self._push_sessions()
            case Route.SESSION_CONFIG:
                self._push_session_config(_expect_params(params, SessionConfigParams))
            case Route.SESSION_CHAT:
                self._push_session_chat(_expect_params(params, SessionChatParams))

    def _push_sessions(self) -> None:
        from tui.screens.sessions.loaders import SessionsLoader
        from tui.screens.sessions.screen import SessionsScreen

        sessions_loader = SessionsLoader(client=self._client)
        screen = SessionsScreen(sessions_loader=sessions_loader)

        self._app.push_screen(screen)

    def _push_session_config(self, params: SessionConfigParams) -> None:
        from tui.screens.session_config.screen import SessionConfigScreen

        screen = SessionConfigScreen(mode=params.mode)

        self._app.push_screen(screen)

    def _push_session_chat(self, params: SessionChatParams) -> None:
        from tui.screens.session_chat.loaders import SessionChatLoader
        from tui.screens.session_chat.screen import SessionChatScreen

        session_chat_loader = SessionChatLoader(client=self._client)
        screen = SessionChatScreen(
            loader=session_chat_loader,
            session_id=params.session_id,
        )

        self._app.push_screen(screen)


def _expect_params[Params](params: object | None, params_type: type[Params]) -> Params:
    if isinstance(params, params_type):
        return params

    raise TypeError(f"Expected navigation params of type {params_type.__name__}")
