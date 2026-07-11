from pydantic import BaseModel

from api.modules.tools.ask_user.models import AskUserAnswerKind


class AskUserAnswerRequest(BaseModel):
    answer_kind: AskUserAnswerKind
    answer: str
