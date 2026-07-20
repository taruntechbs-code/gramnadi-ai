from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.services.exceptions import (
    ConflictError,
    DomainValidationError,
    ResourceNotFoundError,
)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Versioned persistence API for GramNadi AI enterprise resilience data. "
        "Prediction records are stored only; no ML inference is performed."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.exception_handler(ResourceNotFoundError)
async def resource_not_found_handler(
    request: Request, exc: ResourceNotFoundError
) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(ConflictError)
async def conflict_handler(request: Request, exc: ConflictError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(DomainValidationError)
async def domain_validation_handler(
    request: Request, exc: DomainValidationError
) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})
