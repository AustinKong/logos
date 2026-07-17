from asyncio import gather
from uuid import UUID

from api_client.models import AILanguageModelRead, SessionRead, ToolRead, ToolScope
from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.reactive import reactive

from tui.screens.session_config.adapters import (
    form_state_from_config_read,
    form_state_from_session_read,
)
from tui.screens.session_config.controllers import SessionConfigController
from tui.screens.session_config.models import SessionConfigFormState
from tui.screens.session_config.widgets.section_editor import SectionEditor
from tui.widgets.screens.base_modal_screen import BaseModalScreen


class SessionConfigModal(BaseModalScreen[SessionRead | None]):
    BINDINGS = [
        ("escape", "close", "Close"),
        Binding("ctrl+n", "create_config", "Create", key_display="Ctrl+N"),
    ]

    initial_state = reactive[SessionConfigFormState | None](None, recompose=True)

    def __init__(
        self,
        *,
        controller: SessionConfigController,
        session_id: UUID | None = None,
    ) -> None:
        super().__init__()

        self._controller = controller
        self._session_id = session_id
        self._read_only = session_id is not None
        self._models: list[AILanguageModelRead] = []
        self._proposal_tools: list[ToolRead] = []
        self._debate_tools: list[ToolRead] = []
        self.modal_title = "View Session" if self._read_only else "Create Session"

    def compose_content(self) -> ComposeResult:
        if self.initial_state is not None:
            yield SectionEditor(
                form_state=self.initial_state,
                models=self._models,
                proposal_tools=self._proposal_tools,
                debate_tools=self._debate_tools,
                read_only=self._read_only,
            )

    async def on_mount(self) -> None:
        if self.initial_state is None:
            self.content_loading = True
            self.load_config()

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        # Disable create_config in readonly mode
        if action == "create_config":
            return not self._read_only and self.initial_state is not None

        return True

    def action_create_config(self) -> None:
        if self._read_only:
            return

        self.create_config()

    def action_close(self) -> None:
        self.dismiss(None)

    @work(group="session-config", exclusive=True)
    async def load_config(self) -> None:
        try:
            models, proposal_tools, debate_tools = await gather(
                self._controller.list_ai_language_models(),
                self._controller.list_available_tools(scope=ToolScope.PROPOSAL),
                self._controller.list_available_tools(scope=ToolScope.DEBATE),
            )
            if self._session_id is not None:
                session = await self._controller.get_session(session_id=self._session_id)
                form_state = form_state_from_session_read(session)
            else:
                default_config = await self._controller.get_default_config()
                form_state = form_state_from_config_read(default_config, blank_seed=True)
        except Exception as exc:
            self.notify(str(exc), title="Failed to load session config", severity="error")
            self.content_loading = False
            return

        self._models, self._proposal_tools, self._debate_tools = models, proposal_tools, debate_tools
        self.initial_state = form_state
        self.content_loading = False
        self.call_after_refresh(lambda: self.focus_next())

    @work(group="session-config-create", exclusive=True)
    async def create_config(self) -> None:
        try:
            form_state = self.query_one(SectionEditor).form_state()
            session = await self._controller.create_session(form_state)
        except Exception as exc:
            self.notify(str(exc), title="Failed to create session", severity="error")
            return

        self.dismiss(session)
