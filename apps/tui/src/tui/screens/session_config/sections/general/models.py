from attrs import define


@define(frozen=True)
class GeneralFormState:
    prompt: str
    seed: str


@define(frozen=True)
class GeneralCreate:
    prompt: str
    seed: int | None
