from api.modules.engine.models import Token
from api.modules.sessions.schemas.events import TokenRead


def token_read_from_token(token: Token) -> TokenRead:
    return TokenRead(correlation_id=token.correlation_id, content=token.content)
