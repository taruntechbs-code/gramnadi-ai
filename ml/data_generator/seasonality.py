from __future__ import annotations

from dataclasses import dataclass
from typing import Final

import numpy as np

from ml.data_generator.config import EVENT_PROFILES, EventProfile
from ml.data_generator.utils import clamp


@dataclass(frozen=True)
class SeasonalContext:
    month: int
    season: str
    festival_demand_factor: float
    harvest_factor: float
    monsoon_factor: float
    summer_factor: float
    seasonal_income_factor: float
    seasonal_expense_factor: float
    market_event: str
    event_income_factor: float
    event_expense_factor: float
    weather_shock_index: float
    supply_chain_delay_days: int
    commodity_price_multiplier: float


class SeasonalityEngine:
    """Applies recurring Indian rural economic patterns and exogenous events."""

    _SEASONS: Final[dict[int, str]] = {
        1: "winter",
        2: "winter",
        3: "summer",
        4: "summer",
        5: "summer",
        6: "monsoon",
        7: "monsoon",
        8: "monsoon",
        9: "monsoon",
        10: "post_monsoon",
        11: "post_monsoon",
        12: "winter",
    }
    _HARVEST_MONTHS: Final[tuple[int, ...]] = (10, 11, 12, 1, 2, 3)
    _FESTIVAL_MONTHS: Final[tuple[int, ...]] = (9, 10, 11, 12)
    _MONSOON_MONTHS: Final[tuple[int, ...]] = (6, 7, 8, 9)

    def __init__(self, rng: np.random.Generator) -> None:
        self.rng = rng

    def context(self, month: int, sector: str) -> SeasonalContext:
        season = self._SEASONS[month]
        festival_factor = 1.0 + (0.10 if month in self._FESTIVAL_MONTHS else 0.0)
        harvest_factor = 1.12 if month in self._HARVEST_MONTHS else 0.96
        monsoon_factor = 1.08 if month in self._MONSOON_MONTHS else 0.98
        summer_factor = 1.05 if month in (4, 5) else 1.0

        event = self._choose_event(month, sector)
        if event is None:
            event_name = "none"
            income_factor = expense_factor = commodity_factor = 1.0
            weather_shock = 0.0
            delay_days = 0
        else:
            event_name = event.name
            income_factor = event.income_multiplier
            expense_factor = event.expense_multiplier
            commodity_factor = event.commodity_price_multiplier
            weather_shock = event.weather_shock
            delay_days = event.supply_chain_delay_days

        seasonal_income = (
            festival_factor * harvest_factor * monsoon_factor * summer_factor
        )
        seasonal_expense = (1.02 if month in self._MONSOON_MONTHS else 1.0) * (
            1.04 if month in (4, 5) else 1.0
        )
        return SeasonalContext(
            month=month,
            season=season,
            festival_demand_factor=festival_factor,
            harvest_factor=harvest_factor,
            monsoon_factor=monsoon_factor,
            summer_factor=summer_factor,
            seasonal_income_factor=clamp(seasonal_income, 0.75, 1.45),
            seasonal_expense_factor=clamp(seasonal_expense, 0.85, 1.25),
            market_event=event_name,
            event_income_factor=income_factor,
            event_expense_factor=expense_factor,
            weather_shock_index=weather_shock,
            supply_chain_delay_days=delay_days,
            commodity_price_multiplier=commodity_factor,
        )

    def _choose_event(self, month: int, sector: str) -> EventProfile | None:
        probabilities: list[float] = []
        for event in EVENT_PROFILES:
            probability = event.probability
            if event.name == "festival_demand_surge" and month in self._FESTIVAL_MONTHS:
                probability *= 2.8
            if event.name in {"flood", "heavy_rain"} and month in self._MONSOON_MONTHS:
                probability *= 2.2
            if event.name == "drought" and month in (3, 4, 5):
                probability *= 1.8
            if event.name == "disease_outbreak" and sector in {
                "Dairy",
                "Poultry",
                "Fisheries",
                "Goat Farming",
            }:
                probability *= 1.6
            probabilities.append(probability)

        total_probability = sum(probabilities)
        if float(self.rng.random()) >= min(total_probability, 0.95):
            return None
        index = int(
            self.rng.choice(
                len(EVENT_PROFILES), p=np.asarray(probabilities) / total_probability
            )
        )
        return EVENT_PROFILES[index]
