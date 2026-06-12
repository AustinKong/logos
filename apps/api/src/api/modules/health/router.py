from fastapi import APIRouter

from api.modules.health.schemas import HealthCheckResponse

router = APIRouter(tags=["health"])


@router.get("/health", operation_id="getHealth", response_model=HealthCheckResponse)
def health_check() -> HealthCheckResponse:
    return HealthCheckResponse(status="ok")
