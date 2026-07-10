from pydantic import BaseModel, Field, ValidationError

from api.modules.ai.models import AIToolCall, AIToolDefinition
from api.modules.sessions.models.events import Event
from api.modules.tools.ask_user.service import AskUserService
from api.modules.tools.base import ToolExecutionContext
from api.modules.tools.errors import InvalidToolArgumentsError

ASK_USER_TOOL_DEFINITION = AIToolDefinition(
    name="ask_user",
    description=(
        "Ask the user a question when their input is needed to continue. "
        "Provide concise multiple-choice options when there are clear choices."
    ),
    parameters={
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "minLength": 1,
                "description": "The question to ask the user.",
            },
            "options": {
                "type": "array",
                "items": {"type": "string", "minLength": 1},
                "description": "Plain-text multiple-choice options to show to the user.",
            },
        },
        "required": ["question", "options"],
        "additionalProperties": False,
    },
)


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
    def definition(self) -> AIToolDefinition:
        return ASK_USER_TOOL_DEFINITION

    async def execute(self, *, tool_call: AIToolCall, ctx: ToolExecutionContext) -> list[Event]:
        try:
            tool_input = AskUserToolInput.model_validate(tool_call.arguments)
        except ValidationError as exc:
            raise InvalidToolArgumentsError("AI provider returned invalid ask-user arguments") from exc

        return await self._ask_user_service.start(
            session_id=ctx.session_id,
            sender_id=ctx.sender.id,
            question=tool_input.question,
            options=tool_input.options,
        )
