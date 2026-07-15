from attrs import define


@define(frozen=True)
class ProposalFormState:
    tools: list[str]
