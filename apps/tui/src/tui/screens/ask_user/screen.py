from api_client.models import AskUserAnswerKind, AskUserStartedEventRead
from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.widgets import OptionList, Static, TextArea
from textual.widgets.option_list import Option

from tui.screens.ask_user.controllers import AskUserController
from tui.shared.textual import on
from tui.widgets.forms.field import field
from tui.widgets.screens.base_modal_screen import BaseModalScreen


# TODO: Consider whether other modal screens should own submission so they can use content_loading.
class AskUserModal(BaseModalScreen[None]):
    DEFAULT_CSS = """
    AskUserModal #answer {
        height: 5;
    }
    """

    BINDINGS = [
        Binding("ctrl+s", "submit", "Submit", key_display="Ctrl+S"),
        # TODO: Should modals be able to Ctrl Q anyways? this is kept here for easiser debugging since Esc is not valid
        Binding("ctrl+q", "app.pop_screen", "Quit", key_display="Ctrl+Q"),
    ]

    def __init__(self, *, controller: AskUserController, event: AskUserStartedEventRead) -> None:
        super().__init__()
        self._controller = controller
        self._event = event
        self.modal_title = "Input requested"

    def compose_content(self) -> ComposeResult:
        with Vertical():
            yield field("Question", Static(self._event.question))
            yield field(
                "Options",
                OptionList(
                    *(
                        Option(f"{index}. {option}", id=str(index - 1))
                        for index, option in enumerate(self._event.options, 1)
                    ),
                    id="options",
                ),
            )
            yield field(
                "Answer",
                TextArea(
                    placeholder="Type a free-text answer, or select an option",
                    id="answer",
                ),
                helper_text="Select an option to copy it here, or type a free-text answer.",
            )

    @on(OptionList.OptionSelected, "#options")
    def handle_option_selected(self, event: OptionList.OptionSelected) -> None:
        self.query_one("#answer", TextArea).text = self._event.options[event.option_index]

    def action_submit(self) -> None:
        answer = self.query_one("#answer", TextArea).text.strip()
        if not answer:
            self.notify("Answer is required", severity="warning")
            return

        answer_kind = AskUserAnswerKind.OPTION if answer in self._event.options else AskUserAnswerKind.FREE_TEXT
        self.answer_ask_user(answer_kind=answer_kind, answer=answer)

    @work(group="ask-user-answer", exclusive=True)
    async def answer_ask_user(self, *, answer_kind: AskUserAnswerKind, answer: str) -> None:
        self.content_loading = True
        try:
            await self._controller.answer(
                started_event_id=self._event.id,
                answer_kind=answer_kind,
                answer=answer,
            )
        except Exception as exc:
            self.content_loading = False
            self.notify(str(exc), title="Failed to answer question", severity="error")
            return

        self.dismiss(None)
