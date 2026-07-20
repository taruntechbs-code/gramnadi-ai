from fastapi import APIRouter

from app.core.config import settings
from app.schemas.platform import HealthResponse, VersionResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, summary="Check API health")
def health_check() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/version", response_model=VersionResponse, summary="Get API version")
def version_check() -> VersionResponse:
    return VersionResponse(name=settings.app_name, version=settings.app_version)
