from attrs import define


@define(frozen=True)
class GeneralFormState:
    prompt: str
    seed: str
    debate_round_count: str


@define(frozen=True)
class GeneralCreate:
    prompt: str
    seed: int | None
    debate_round_count: int
