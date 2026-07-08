from api.modules.ai.models import Verbosity

BASE_STYLE_PROMPT_INSTRUCTION = (
    "Style: write in plain conversational prose. Do not use markdown formatting, headings, or bullet lists unless "
    "the user explicitly asks for them."
)

VERBOSITY_PROMPT_INSTRUCTIONS = {
    Verbosity.LOW: "Verbosity: keep it very brief. Usually one short paragraph is enough.",
    Verbosity.MEDIUM: "Verbosity: keep it compact. Use 2-4 short paragraphs and only the most important reasoning.",
    Verbosity.HIGH: "Verbosity: be thorough, but stay conversational. Include key tradeoffs, assumptions, and edge cases.",
}


def response_prompt_instruction(verbosity: Verbosity) -> str:
    return f"{BASE_STYLE_PROMPT_INSTRUCTION}\n\n{VERBOSITY_PROMPT_INSTRUCTIONS[verbosity]}"
