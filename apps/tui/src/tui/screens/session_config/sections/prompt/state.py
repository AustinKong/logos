from attrs import define


@define(frozen=True)
class PromptFormState:
    value: str
