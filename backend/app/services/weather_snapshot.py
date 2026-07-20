from app.models.weather_snapshot import WeatherSnapshot
from app.schemas.weather_snapshot import WeatherSnapshotCreate, WeatherSnapshotUpdate
from app.services.base import CRUDService


class WeatherSnapshotService(
    CRUDService[WeatherSnapshot, WeatherSnapshotCreate, WeatherSnapshotUpdate]
):
    model = WeatherSnapshot
    resource_name = "weather snapshot"
