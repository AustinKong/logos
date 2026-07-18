import re

from pydantic import BaseModel, Field, ValidationError

from api.modules.ai.models import AIToolCall
from api.modules.sessions.models.events import Event
from api.modules.tools.ask_user.definition import ASK_USER_TOOL_DEFINITION
from api.modules.tools.ask_user.service import AskUserService
from api.modules.tools.base import ToolExecutionContext
from api.modules.tools.errors import InvalidToolArgumentsError
from api.modules.tools.models import ToolDefinition

# Strip option labels like "A)", "B.", "1.", "2)".
OPTION_LABEL_PATTERN = re.compile(r"^\s*(?:[A-Za-z]|\d+)[.)]\s+")


# TODO: If its possible to define parameters as ask user tool input and conver to the json needed
class AskUserToolInput(BaseModel):
    question: str = Field(min_length=1)
    options: list[str] = Field(min_length=1)


class AskUserTool:
    def __init__(
        self,
        *,
        ask_user_service: AskUserService,
    ) -> None:
        self._ask_user_service = ask_user_service

    @property
    def definition(self) -> ToolDefinition:
        return ASK_USER_TOOL_DEFINITION

    async def execute(self, *, tool_call: AIToolCall, ctx: ToolExecutionContext) -> list[Event]:
        try:
            tool_input = AskUserToolInput.model_validate(tool_call.arguments)
        except ValidationError as exc:
            raise InvalidToolArgumentsError("AI provider returned invalid ask-user arguments") from exc

        return await self._ask_user_service.start(
            session_id=ctx.session_id,
            question=tool_input.question,
            options=[OPTION_LABEL_PATTERN.sub("", option) for option in tool_input.options],
        )
