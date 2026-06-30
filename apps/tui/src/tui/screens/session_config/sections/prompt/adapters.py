from tui.screens.session_config.errors import SessionConfigValidationError
from tui.screens.session_config.sections.prompt.state import PromptFormState


def prompt_form_state_from_read(prompt: str) -> PromptFormState:
    return PromptFormState(value=prompt)


def prompt_create_from_form_state(state: PromptFormState) -> str:
    if not state.value.strip():
        raise SessionConfigValidationError("Prompt is required")

    return state.value
