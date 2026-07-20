from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ml.data_generator.config import LocationProfile
from ml.data_generator.seasonality import SeasonalContext
from ml.data_generator.utils import clamp


@dataclass(frozen=True)
class CommoditySnapshot:
    prices: dict[str, float]
    price_pressure: float


class CommodityEngine:
    """Generates correlated, seasonally adjusted commodity prices in INR."""

    _BASE_PRICES = {
        "milk": 52.0,
        "feed": 34.0,
        "grains": 31.0,
        "vegetables": 28.0,
        "fish_feed": 48.0,
        "fuel": 96.0,
        "electricity": 8.5,
    }

    def __init__(self, rng: np.random.Generator, noise_std: float) -> None:
        self.rng = rng
        self.noise_std = noise_std

    def generate(
        self,
        location: LocationProfile,
        month: int,
        seasonal: SeasonalContext,
        sector_commodities: tuple[str, ...],
    ) -> CommoditySnapshot:
        stable_district_code = sum(
            (position + 1) * ord(character)
            for position, character in enumerate(location.district)
        )
        regional_factor = 1.0 + (stable_district_code % 7 - 3) * 0.008
        prices: dict[str, float] = {}
        for commodity, base_price in self._BASE_PRICES.items():
            seasonal_factor = self._seasonal_factor(commodity, month)
            event_factor = seasonal.commodity_price_multiplier
            noise_factor = max(
                0.85, 1.0 + float(self.rng.normal(0.0, self.noise_std * 0.7))
            )
            price = (
                base_price
                * regional_factor
                * seasonal_factor
                * event_factor
                * noise_factor
            )
            prices[commodity] = round(max(0.1, price), 2)

        pressure = (
            np.mean(
                [prices[name] / self._BASE_PRICES[name] for name in sector_commodities]
            )
            if sector_commodities
            else 1.0
        )
        return CommoditySnapshot(
            prices=prices,
            price_pressure=round(clamp(float(pressure), 0.65, 1.8), 4),
        )

    @staticmethod
    def _seasonal_factor(commodity: str, month: int) -> float:
        if commodity == "vegetables":
            return 1.12 if month in (5, 6) else 0.94 if month in (11, 12, 1) else 1.0
        if commodity == "grains":
            return 0.92 if month in (3, 4) else 1.08 if month in (8, 9) else 1.0
        if commodity == "feed":
            return 1.08 if month in (5, 6, 7) else 0.96 if month in (11, 12) else 1.0
        if commodity == "fish_feed":
            return 1.10 if month in (6, 7, 8) else 0.97
        if commodity == "fuel":
            return 1.04 if month in (4, 5, 6) else 1.0
        if commodity == "electricity":
            return 1.12 if month in (4, 5, 6) else 0.96 if month in (11, 12, 1) else 1.0
        return 1.02 if month in (4, 5) else 0.99 if month in (7, 8) else 1.0
