from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widgets import Label


class FooterKV(Horizontal):
    DEFAULT_CSS = """
    FooterKV {
        width: auto;
        height: 1;
    }

    FooterKV .key {
        color: $text;
        text-style: bold;
    }

    FooterKV .value {
        color: $text-muted;
        padding: 0 1;
    }
    """

    def __init__(self, key: str, value: str) -> None:
        super().__init__()
        self.key = key
        self.value = value

    def compose(self) -> ComposeResult:
        yield Label(self.key, classes="key")
        yield Label(self.value, classes="value")


class Footer(Horizontal):
    """A simpler implementation of Textual's Footer widget with style overrides."""

    DEFAULT_CSS = """
    Footer {
        dock: bottom;
        height: 1;
        layout: horizontal;
    }
    """

    refresh_counter = reactive(0)

    def compose(self) -> ComposeResult:
        yield from self._binding_widgets()

    def on_mount(self) -> None:
        self.screen.bindings_updated_signal.subscribe(
            self,
            self._bindings_changed,
        )

    def on_unmount(self) -> None:
        self.screen.bindings_updated_signal.unsubscribe(self)

    def _bindings_changed(self, _screen) -> None:
        self.call_after_refresh(self.recompose)

    def _binding_widgets(self):
        seen_actions: set[str] = set()

        for _, binding, enabled, _tooltip in self.screen.active_bindings.values():
            if not binding.show or not enabled:
                continue

            if binding.action in seen_actions:
                continue

            seen_actions.add(binding.action)

            yield FooterKV(
                self.app.get_key_display(binding),
                binding.description,
            )
