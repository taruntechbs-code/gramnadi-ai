from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class TimeSplit:
    train: pd.DataFrame
    validation: pd.DataFrame
    test: pd.DataFrame
    boundaries: dict[str, Any]


class TimeAwareSplitter:
    """Splits complete calendar months chronologically without shuffling."""

    def __init__(
        self, train_ratio: float, validation_ratio: float, test_ratio: float
    ) -> None:
        self.train_ratio = train_ratio
        self.validation_ratio = validation_ratio
        self.test_ratio = test_ratio

    def split(self, frame: pd.DataFrame) -> TimeSplit:
        ordered = frame.sort_values(["month_date", "enterprise_id"]).reset_index(
            drop=True
        )
        months = pd.Series(
            ordered["month_date"].drop_duplicates().sort_values().to_list()
        )
        if len(months) < 3:
            raise ValueError(
                "At least three unique months are required for a time split"
            )
        train_end = max(1, int(len(months) * self.train_ratio))
        validation_end = max(
            train_end + 1,
            int(len(months) * (self.train_ratio + self.validation_ratio)),
        )
        validation_end = min(validation_end, len(months) - 1)
        train_months = set(months.iloc[:train_end])
        validation_months = set(months.iloc[train_end:validation_end])
        test_months = set(months.iloc[validation_end:])
        train = ordered[ordered["month_date"].isin(train_months)].copy()
        validation = ordered[ordered["month_date"].isin(validation_months)].copy()
        test = ordered[ordered["month_date"].isin(test_months)].copy()
        self._validate(train, validation, test)
        boundaries = {
            "train_start": str(months.iloc[0]),
            "train_end": str(months.iloc[train_end - 1]),
            "validation_start": str(months.iloc[train_end]),
            "validation_end": str(months.iloc[validation_end - 1]),
            "test_start": str(months.iloc[validation_end]),
            "test_end": str(months.iloc[-1]),
            "month_counts": {
                "train": int(len(train_months)),
                "validation": int(len(validation_months)),
                "test": int(len(test_months)),
            },
        }
        return TimeSplit(
            train.reset_index(drop=True),
            validation.reset_index(drop=True),
            test.reset_index(drop=True),
            boundaries,
        )

    @staticmethod
    def _validate(
        train: pd.DataFrame, validation: pd.DataFrame, test: pd.DataFrame
    ) -> None:
        train_dates = set(train["month_date"])
        validation_dates = set(validation["month_date"])
        test_dates = set(test["month_date"])
        if (
            train_dates & validation_dates
            or train_dates & test_dates
            or validation_dates & test_dates
        ):
            raise ValueError("Time split contains overlapping months")
        if not (
            train["month_date"].max()
            < validation["month_date"].min()
            < test["month_date"].min()
        ):
            raise ValueError("Time split is not strictly chronological")
        for subset in (train, validation, test):
            for _, group in subset.groupby("enterprise_id", sort=False):
                if not group["month_date"].is_monotonic_increasing:
                    raise ValueError(
                        "Enterprise sequence was not preserved within a split"
                    )
