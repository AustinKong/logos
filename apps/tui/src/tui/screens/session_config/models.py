from enum import StrEnum


class ConfigSection(StrEnum):
    PROMPT = "prompt"
    TURN_SELECTION = "turn_selection"
    CONTEXT = "context"
    VALIDATION = "validation"
    RESOLUTION = "resolution"
    PARTICIPANTS = "participants"
