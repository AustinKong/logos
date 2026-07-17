from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from typing import assert_never
from uuid import UUID

from api_client import Client
from api_client.models import AILanguageModelRead, AskUserStartedEventRead, SessionRead
from textual.app import App
from textual.message import Message

from tui.screens.participant_editor.models import ParticipantFormState


class Route(StrEnum):
    SESSIONS = "sessions"
    SESSION_CONFIG = "session_config"
    SESSION_CHAT = "session_chat"
    ASK_USER = "ask_user"
    PARTICIPANT_EDITOR = "participant_editor"


@dataclass(frozen=True, slots=True)
class SessionConfigParams:
    session_id: UUID | None = None
    on_close: Callable[[SessionRead | None], None] | None = None


@dataclass(frozen=True, slots=True)
class SessionChatParams:
    session_id: UUID


@dataclass(frozen=True, slots=True)
class AskUserParams:
    event: AskUserStartedEventRead
    on_close: Callable[[None], None]


@dataclass(frozen=True, slots=True)
class ParticipantEditorParams:
    initial_state: ParticipantFormState
    models: list[AILanguageModelRead]
    read_only: bool
    on_close: Callable[[ParticipantFormState], None]


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
            case Route.ASK_USER:
                self._push_ask_user(_expect_params(params, AskUserParams))
            case Route.PARTICIPANT_EDITOR:
                self._push_participant_editor(_expect_params(params, ParticipantEditorParams))
            case _ as never:
                assert_never(never)

    def _push_sessions(self) -> None:
        from tui.screens.sessions.loaders import SessionsLoader
        from tui.screens.sessions.screen import SessionsScreen

        sessions_loader = SessionsLoader(client=self._client)
        screen = SessionsScreen(sessions_loader=sessions_loader)

        self._app.push_screen(screen)

    def _push_session_config(self, params: SessionConfigParams) -> None:
        from tui.screens.session_config.controllers import SessionConfigController
        from tui.screens.session_config.screen import SessionConfigModal

        session_config_controller = SessionConfigController(client=self._client)
        screen = SessionConfigModal(
            controller=session_config_controller,
            session_id=params.session_id,
        )

        self._app.push_screen(
            screen,
            None if params.on_close is None else params.on_close,
        )

    def _push_session_chat(self, params: SessionChatParams) -> None:
        from tui.screens.session_chat.controllers import SessionChatController
        from tui.screens.session_chat.loaders import SessionChatLoader
        from tui.screens.session_chat.screen import SessionChatScreen

        session_chat_controller = SessionChatController(client=self._client)
        session_chat_loader = SessionChatLoader(client=self._client)
        screen = SessionChatScreen(
            controller=session_chat_controller,
            loader=session_chat_loader,
            session_id=params.session_id,
        )

        self._app.push_screen(screen)

    def _push_ask_user(self, params: AskUserParams) -> None:
        from tui.screens.ask_user.controllers import AskUserController
        from tui.screens.ask_user.screen import AskUserModal

        ask_user_controller = AskUserController(client=self._client)
        screen = AskUserModal(
            controller=ask_user_controller,
            event=params.event,
        )

        self._app.push_screen(screen, params.on_close)

    def _push_participant_editor(self, params: ParticipantEditorParams) -> None:
        from tui.screens.participant_editor.screen import ParticipantEditorModal

        screen = ParticipantEditorModal(
            initial_state=params.initial_state,
            models=params.models,
            read_only=params.read_only,
        )

        def handle_closed(
            participant: ParticipantFormState | None,
            on_close: Callable[[ParticipantFormState], None],
        ) -> None:
            if participant is not None:
                on_close(participant)

        self._app.push_screen(screen, lambda result: handle_closed(result, params.on_close))


def _expect_params[Params](params: object | None, params_type: type[Params]) -> Params:
    if isinstance(params, params_type):
        return params

    raise TypeError(f"Expected navigation params of type {params_type.__name__}")
