from api.modules.engine.models import Token
from api.modules.engine.schemas import TokenRead


def token_read_from_token(token: Token) -> TokenRead:
    return TokenRead(stream_id=token.stream_id, content=token.content)
