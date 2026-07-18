from api.modules.tools.models import ToolDefinition, ToolScope

ASK_USER_TOOL_DEFINITION = ToolDefinition(
    name="ask_user",
    title="Ask user",
    user_description="Request input from the user before the session can continue.",
    ai_description=(
        "Ask the user a question when their input is needed to continue. "
        "Provide concise multiple-choice options when there are clear choices."
    ),
    scopes=frozenset({ToolScope.PROPOSAL, ToolScope.DEBATE}),
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
                "description": "Plain-text options without labels or prefixes such as A), B), 1., or 2.",
            },
        },
        "required": ["question", "options"],
        "additionalProperties": False,
    },
)
