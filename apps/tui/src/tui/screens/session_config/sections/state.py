from textual.widgets._select import NoSelection

type SelectValue = str | NoSelection


def state_or_default[StateT](state: object, state_type: type[StateT], default_state: StateT) -> StateT:
    if isinstance(state, state_type):
        return state

    return default_state
