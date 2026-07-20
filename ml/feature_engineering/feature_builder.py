from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from ml.feature_engineering.config import TARGET_COLUMNS
from ml.feature_engineering.utils import safe_divide


@dataclass(frozen=True)
class FeatureBuildResult:
    frame: pd.DataFrame
    added_features: tuple[str, ...]
    leakage_columns: tuple[str, ...]


class FeatureBuilder:
    """Builds causal, enterprise-grouped features from the Phase 2 panel."""

    def __init__(self, rolling_windows: tuple[int, ...] = (3, 6, 12)) -> None:
        self.rolling_windows = rolling_windows

    def build(self, frame: pd.DataFrame) -> FeatureBuildResult:
        result = (
            frame.sort_values(["enterprise_id", "month_date"])
            .reset_index(drop=True)
            .copy()
        )
        before = set(result.columns)
        grouped = result.groupby("enterprise_id", sort=False)

        self._add_time_features(result)
        self._add_financial_features(result, grouped)
        self._add_weather_features(result, grouped)
        self._add_commodity_features(result, grouped)
        self._add_enterprise_features(result, grouped)
        self._add_lag_features(result, grouped)
        self._add_rolling_features(result, grouped)
        self._add_interaction_features(result)

        added = tuple(column for column in result.columns if column not in before)
        leakage = tuple(
            column
            for column in result.columns
            if column in TARGET_COLUMNS
            or column in {"risk_factors", "risk_x_cash_flow"}
            or "after_" in column
        )
        return FeatureBuildResult(result, added, leakage)

    @staticmethod
    def _add_time_features(frame: pd.DataFrame) -> None:
        frame["quarter"] = frame["month_date"].dt.quarter.astype("int8")
        frame["monsoon_indicator"] = frame["month"].isin([6, 7, 8, 9]).astype("int8")
        frame["festival_season_flag"] = (
            frame["month"].isin([9, 10, 11, 12]).astype("int8")
        )
        frame["year_end_indicator"] = frame["month"].eq(12).astype("int8")

    @staticmethod
    def _add_financial_features(frame: pd.DataFrame, grouped: Any) -> None:
        frame["profit_margin"] = safe_divide(frame["profit"], frame["income"])
        frame["expense_ratio"] = safe_divide(frame["expense"], frame["income"])
        frame["savings_ratio"] = safe_divide(frame["savings"], frame["income"])
        frame["loan_to_income_ratio"] = safe_divide(
            frame["outstanding_loan"], frame["income"]
        )
        frame["debt_service_ratio_feature"] = safe_divide(
            frame["monthly_installment"], frame["income"]
        )
        frame["revenue_growth_pct"] = (
            grouped["income"]
            .pct_change()
            .replace([np.inf, -np.inf], np.nan)
            .fillna(0.0)
        )
        frame["expense_growth_pct"] = (
            grouped["expense"]
            .pct_change()
            .replace([np.inf, -np.inf], np.nan)
            .fillna(0.0)
        )
        frame["cash_flow_growth_pct"] = (
            grouped["net_cash_flow"]
            .pct_change()
            .replace([np.inf, -np.inf], np.nan)
            .fillna(0.0)
        )
        frame["inventory_turnover_proxy"] = safe_divide(
            frame["expense"], frame["inventory_value"]
        )
        frame["credit_utilization_proxy"] = safe_divide(
            frame["outstanding_loan"], frame["principal_amount"]
        )

    @staticmethod
    def _add_weather_features(frame: pd.DataFrame, grouped: Any) -> None:
        climatology = frame.groupby(["district", "month"])["rainfall"].transform("mean")
        temperature_climatology = frame.groupby(["district", "month"])[
            "temperature"
        ].transform("mean")
        frame["rainfall_anomaly"] = frame["rainfall"] - climatology
        frame["temperature_anomaly"] = frame["temperature"] - temperature_climatology
        frame["rainfall_rolling_mean"] = grouped["rainfall"].transform(
            lambda values: values.rolling(3, min_periods=1).mean()
        )
        frame["temperature_rolling_mean"] = grouped["temperature"].transform(
            lambda values: values.rolling(3, min_periods=1).mean()
        )
        frame["weather_severity_index"] = (
            (
                frame["weather_shock_index"]
                + frame["rainfall_anomaly"].abs()
                / frame["rainfall_rolling_mean"].replace(0, np.nan)
            )
            .replace([np.inf, -np.inf], np.nan)
            .fillna(frame["weather_shock_index"])
        )

    @staticmethod
    def _add_commodity_features(frame: pd.DataFrame, grouped: Any) -> None:
        price_columns = [
            column
            for column in (
                "milk_price",
                "feed_price",
                "grains_price",
                "vegetables_price",
                "fish_feed_price",
                "fuel_price",
                "electricity_price",
            )
            if column in frame.columns
        ]
        frame["commodity_price_index"] = frame[price_columns].mean(axis=1)
        frame["commodity_price_moving_average"] = grouped[
            "commodity_price_index"
        ].transform(lambda values: values.rolling(3, min_periods=1).mean())
        frame["commodity_price_trend"] = (
            grouped["commodity_price_index"]
            .pct_change()
            .replace([np.inf, -np.inf], np.nan)
            .fillna(0.0)
        )
        frame["commodity_price_volatility"] = (
            grouped["commodity_price_index"]
            .transform(lambda values: values.rolling(3, min_periods=1).std(ddof=0))
            .fillna(0.0)
        )
        frame["commodity_price_momentum"] = safe_divide(
            frame["commodity_price_index"] - frame["commodity_price_moving_average"],
            frame["commodity_price_moving_average"],
        )

    @staticmethod
    def _add_enterprise_features(frame: pd.DataFrame, grouped: Any) -> None:
        frame["enterprise_age_months"] = (
            (frame["month_date"] - frame["business_start_date"]).dt.days / 30.4375
        ).clip(lower=0)
        frame["years_in_business"] = frame["enterprise_age_months"] / 12.0
        active_loan = frame["outstanding_loan"].gt(0)
        frame["loan_age_months"] = active_loan.groupby(frame["enterprise_id"]).cumsum()
        frame["historical_intervention_count"] = 0
        if "loan_default_flag" in frame:
            cumulative_defaults = grouped["loan_default_flag"].cumsum()
            frame["previous_default_count"] = (
                cumulative_defaults.groupby(frame["enterprise_id"], sort=False)
                .shift(1)
                .fillna(0)
            )
        else:
            frame["previous_default_count"] = 0
        frame["historical_average_revenue"] = (
            grouped["income"]
            .transform(lambda values: values.shift(1).expanding(min_periods=1).mean())
            .fillna(frame["income"])
        )
        frame["historical_average_expenses"] = (
            grouped["expense"]
            .transform(lambda values: values.shift(1).expanding(min_periods=1).mean())
            .fillna(frame["expense"])
        )
        frame["historical_average_cash_flow"] = (
            grouped["net_cash_flow"]
            .transform(lambda values: values.shift(1).expanding(min_periods=1).mean())
            .fillna(frame["net_cash_flow"])
        )

    @staticmethod
    def _add_lag_features(frame: pd.DataFrame, grouped: Any) -> None:
        lag_map = {
            "income": (1, 3),
            "expense": (1,),
            "net_cash_flow": (1, 3, 6),
            "risk_score": (1,),
        }
        for source, lags in lag_map.items():
            for lag in lags:
                column = f"{source}_lag_{lag}"
                frame[column] = grouped[source].shift(lag).fillna(frame[source])

    def _add_rolling_features(self, frame: pd.DataFrame, grouped: Any) -> None:
        rolling_specs = {
            "income": "revenue",
            "expense": "expense",
            "net_cash_flow": "cashflow",
        }
        for window in self.rolling_windows:
            for source, label in rolling_specs.items():
                frame[f"{window}_month_{label}_mean"] = grouped[source].transform(
                    lambda values, size=window: values.rolling(
                        size, min_periods=1
                    ).mean()
                )
                if source in {"income", "net_cash_flow"}:
                    frame[f"{window}_month_{label}_std"] = (
                        grouped[source]
                        .transform(
                            lambda values, size=window: values.rolling(
                                size, min_periods=1
                            ).std(ddof=0)
                        )
                        .fillna(0.0)
                    )
            if window == 6:
                frame["6_month_rolling_trend"] = (
                    grouped["income"]
                    .transform(
                        lambda values: values.pct_change(6).replace(
                            [np.inf, -np.inf], np.nan
                        )
                    )
                    .fillna(0.0)
                )
                frame["6_month_rolling_volatility"] = (
                    grouped["net_cash_flow"]
                    .transform(
                        lambda values: values.rolling(6, min_periods=1).std(ddof=0)
                    )
                    .fillna(0.0)
                )

    @staticmethod
    def _add_interaction_features(frame: pd.DataFrame) -> None:
        frame["weather_x_commodity"] = (
            frame["weather_severity_index"] * frame["commodity_price_pressure"]
        )
        frame["weather_x_sector"] = (
            frame["sector"].astype(str) + "__" + frame["weather_condition"].astype(str)
        )
        frame["season_x_revenue"] = frame["seasonal_income_factor"] * frame["income"]
        frame["loan_x_revenue"] = frame["outstanding_loan"] * frame["income"]
        frame["risk_x_cash_flow"] = frame["risk_score"] * frame["net_cash_flow"]
        frame["commodity_x_inventory"] = (
            frame["commodity_price_pressure"] * frame["inventory_value"]
        )
