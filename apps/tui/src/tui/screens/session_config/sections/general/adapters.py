from tui.screens.session_config.errors import SessionConfigValidationError
from tui.screens.session_config.sections.general.models import GeneralCreate, GeneralFormState


def general_form_state_from_read(prompt: str, seed: str, debate_round_count: str) -> GeneralFormState:
    return GeneralFormState(prompt=prompt, seed=seed, debate_round_count=debate_round_count)


def general_create_from_form_state(state: GeneralFormState) -> GeneralCreate:
    return GeneralCreate(
        prompt=_prompt_create_from_form_state(state),
        seed=_seed_create_from_form_state(state),
        debate_round_count=_debate_round_count_create_from_form_state(state),
    )


def _prompt_create_from_form_state(state: GeneralFormState) -> str:
    if not state.prompt.strip():
        raise SessionConfigValidationError("Prompt is required")

    return state.prompt


def _seed_create_from_form_state(state: GeneralFormState) -> int | None:
    if not state.seed.strip():
        return None

    try:
        return int(state.seed)
    except ValueError as exc:
        raise SessionConfigValidationError("Seed must be a whole number") from exc


def _debate_round_count_create_from_form_state(state: GeneralFormState) -> int:
    try:
        debate_round_count = int(state.debate_round_count)
    except ValueError as exc:
        raise SessionConfigValidationError("Debate rounds must be a whole number") from exc

    if debate_round_count < 1:
        raise SessionConfigValidationError("Debate rounds must be at least 1")

    return debate_round_count
