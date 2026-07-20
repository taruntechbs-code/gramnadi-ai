from __future__ import annotations

from collections.abc import Iterable
from datetime import date
from math import isfinite
from typing import TypeVar

import numpy as np

T = TypeVar("T")


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    if denominator == 0:
        return default
    return numerator / denominator


def noisy_multiplier(rng: np.random.Generator, standard_deviation: float) -> float:
    return max(0.01, 1.0 + float(rng.normal(0.0, standard_deviation)))


def choose_weighted(
    rng: np.random.Generator, values: Iterable[T], weights: Iterable[float]
) -> T:
    choices = tuple(values)
    probabilities = np.asarray(tuple(weights), dtype=float)
    if not choices or len(choices) != len(probabilities):
        raise ValueError("values and weights must be non-empty and equally sized")
    if np.any(probabilities < 0) or not isfinite(float(probabilities.sum())):
        raise ValueError("weights must be finite and non-negative")
    if probabilities.sum() == 0:
        probabilities = np.ones(len(choices), dtype=float)
    probabilities = probabilities / probabilities.sum()
    return choices[int(rng.choice(len(choices), p=probabilities))]


def month_dates(start_date: date, count: int) -> list[date]:
    dates: list[date] = []
    year, month = start_date.year, start_date.month
    for _ in range(count):
        dates.append(date(year, month, 1))
        month += 1
        if month == 13:
            year += 1
            month = 1
    return dates


def percent_change(current: float, previous: float) -> float:
    return safe_divide(current - previous, abs(previous), default=0.0)
