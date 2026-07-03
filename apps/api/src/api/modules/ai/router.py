from typing import Annotated

from fastapi import APIRouter, Depends

from api.modules.ai.deps import get_ai_service
from api.modules.ai.schemas import AIModelRead
from api.modules.ai.service import AIService

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/models", operation_id="listAIModels", response_model=list[AIModelRead])
def list_ai_models(
    service: Annotated[AIService, Depends(get_ai_service)],
) -> list[AIModelRead]:
    return [
        AIModelRead(
            id=model.id,
            label=model.label,
            provider=model.provider,
            supports_reasoning=model.supports_reasoning,
        )
        for model in service.list_available_models()
    ]
