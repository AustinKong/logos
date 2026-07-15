from api_client.models import ProposalConfigCreate, ProposalConfigRead

from tui.screens.session_config.sections.proposal.models import ProposalFormState


def proposal_form_state_from_read(config: ProposalConfigRead) -> ProposalFormState:
    return ProposalFormState(tools=config.tools)


def proposal_create_from_form_state(state: ProposalFormState) -> ProposalConfigCreate:
    return ProposalConfigCreate(tools=state.tools)
