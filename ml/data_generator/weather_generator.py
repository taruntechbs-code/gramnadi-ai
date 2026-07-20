from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ml.data_generator.config import LocationProfile
from ml.data_generator.seasonality import SeasonalContext
from ml.data_generator.utils import clamp


@dataclass(frozen=True)
class WeatherSnapshot:
    temperature: float
    rainfall: float
    humidity: float
    condition: str
    shock_index: float


class WeatherEngine:
    """Generates climate-aware monthly weather for each district profile."""

    def __init__(self, rng: np.random.Generator, noise_std: float) -> None:
        self.rng = rng
        self.noise_std = noise_std

    def generate(
        self, location: LocationProfile, month: int, seasonal: SeasonalContext
    ) -> WeatherSnapshot:
        temperature = location.mean_temperature_c + self._temperature_cycle(
            location, month
        )
        temperature += float(self.rng.normal(0.0, 0.8 + self.noise_std * 2))

        in_monsoon = month in location.monsoon_months
        expected_rainfall = (
            location.monsoon_rainfall_mm if in_monsoon else location.dry_rainfall_mm
        )
        rainfall = max(0.0, expected_rainfall * float(self.rng.lognormal(0.0, 0.28)))
        if seasonal.market_event == "drought":
            rainfall *= 0.22
        elif seasonal.market_event in {"flood", "heavy_rain"}:
            rainfall *= 1.75 if seasonal.market_event == "flood" else 1.45

        humidity = location.humidity_base + (18.0 if rainfall > 80 else -8.0)
        humidity += float(self.rng.normal(0.0, 3.0))
        humidity = clamp(humidity, 18.0, 98.0)

        condition = self._condition(rainfall, temperature, seasonal.market_event)
        excess_rain = max(0.0, rainfall / max(expected_rainfall, 1.0) - 1.0)
        rainfall_deficit = max(0.0, 1.0 - rainfall / max(expected_rainfall, 1.0))
        shock = clamp(
            seasonal.weather_shock_index + excess_rain * 0.35 + rainfall_deficit * 0.18,
            0.0,
            1.0,
        )
        return WeatherSnapshot(
            temperature=round(temperature, 2),
            rainfall=round(rainfall, 2),
            humidity=round(humidity, 2),
            condition=condition,
            shock_index=round(shock, 4),
        )

    @staticmethod
    def _temperature_cycle(location: LocationProfile, month: int) -> float:
        phase = (month - 4) / 12.0 * 2.0 * np.pi
        return location.temperature_amplitude_c * float(np.sin(phase))

    @staticmethod
    def _condition(rainfall: float, temperature: float, event: str) -> str:
        if event == "flood" or rainfall >= 260:
            return "flood"
        if event == "heavy_rain" or rainfall >= 150:
            return "heavy_rain"
        if rainfall >= 45:
            return "rain"
        if temperature >= 35:
            return "hot"
        if rainfall <= 8:
            return "dry"
        return "partly_cloudy"
