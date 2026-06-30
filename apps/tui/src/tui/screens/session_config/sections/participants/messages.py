from textual.message import Message


class NewParticipant(Message):
    pass


class RemoveParticipant(Message):
    pass


class ParticipantNameChanged(Message):
    def __init__(self, participant_key: str, name: str) -> None:
        super().__init__()
        self.participant_key = participant_key
        self.name = name
