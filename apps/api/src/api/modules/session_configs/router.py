from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from api.modules.session_configs.adapters.session_configs import session_config_read_from_config
from api.modules.session_configs.deps import get_session_config_service
from api.modules.session_configs.schemas.session_configs import SessionConfigRead
from api.modules.session_configs.service import SessionConfigService

router = APIRouter(prefix="/session-configs", tags=["session-configs"])


@router.get("/default", operation_id="getDefaultSessionConfig", response_model=SessionConfigRead)
async def get_default_session_config(
    service: Annotated[SessionConfigService, Depends(get_session_config_service)],
) -> SessionConfigRead:
    return session_config_read_from_config(await service.get_default_config())


@router.get("/{config_id}", operation_id="getSessionConfig", response_model=SessionConfigRead)
async def get_session_config(
    config_id: UUID,
    service: Annotated[SessionConfigService, Depends(get_session_config_service)],
) -> SessionConfigRead:
    return session_config_read_from_config(await service.get_config(config_id))
