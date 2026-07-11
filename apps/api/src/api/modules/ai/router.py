from typing import Annotated

from fastapi import APIRouter, Depends

from api.modules.ai.deps import get_ai_service
from api.modules.ai.schemas import AIEmbeddingModelRead, AILanguageModelRead
from api.modules.ai.service import AIService

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/language-models", operation_id="listAILanguageModels", response_model=list[AILanguageModelRead])
def list_ai_language_models(
    service: Annotated[AIService, Depends(get_ai_service)],
) -> list[AILanguageModelRead]:
    return [
        AILanguageModelRead(
            id=model.id,
            label=model.label,
            provider=model.provider,
            supports_reasoning=model.supports_reasoning,
        )
        for model in service.list_available_language_models()
    ]


@router.get("/embedding-models", operation_id="listAIEmbeddingModels", response_model=list[AIEmbeddingModelRead])
def list_ai_embedding_models(
    service: Annotated[AIService, Depends(get_ai_service)],
) -> list[AIEmbeddingModelRead]:
    return [
        AIEmbeddingModelRead(
            id=model.id,
            label=model.label,
            provider=model.provider,
        )
        for model in service.list_available_embedding_models()
    ]
