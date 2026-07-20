from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.graph.graph_service import GraphService
from app.ml.loader import ModelLoader
from app.services.exceptions import (
    ConflictError,
    DomainValidationError,
    ResourceNotFoundError,
)

model_loader = ModelLoader()
graph_service = GraphService()


@asynccontextmanager
async def lifespan(application: FastAPI):
    try:
        model_loader.load()
    except Exception:
        # Keep the API available for health diagnostics; ML routes return 503.
        pass
    application.state.model_loader = model_loader
    try:
        graph_service.load()
    except Exception:
        # Keep the API available for graph diagnostics if source data is unavailable.
        pass
    application.state.graph_service = graph_service
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Versioned persistence API for GramNadi AI enterprise resilience data. "
        "Prediction records are stored only; no ML inference is performed."
    ),
    lifespan=lifespan,
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
