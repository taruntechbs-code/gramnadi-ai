from app.api.v1.routes.crud import build_crud_router
from app.schemas.weather_snapshot import (
    WeatherSnapshotCreate,
    WeatherSnapshotResponse,
    WeatherSnapshotUpdate,
)
from app.services.weather_snapshot import WeatherSnapshotService

router = build_crud_router(
    resource_path="weather-snapshots",
    resource_name="weather snapshot",
    tag="Weather Snapshots",
    create_schema=WeatherSnapshotCreate,
    update_schema=WeatherSnapshotUpdate,
    response_schema=WeatherSnapshotResponse,
    service_factory=WeatherSnapshotService,
)
