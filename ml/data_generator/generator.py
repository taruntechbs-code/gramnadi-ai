from __future__ import annotations

import argparse
from collections.abc import Iterable
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from ml.data_generator.commodity_generator import CommodityEngine
from ml.data_generator.config import SECTOR_PROFILES, GeneratorConfig
from ml.data_generator.enterprise_generator import (
    EnterpriseContext,
    EnterpriseGenerator,
)
from ml.data_generator.export import export_dataset, generate_analysis_report
from ml.data_generator.finance_generator import FinanceEngine, FinanceSnapshot
from ml.data_generator.loan_generator import LoanEngine, LoanState
from ml.data_generator.risk_engine import RiskEngine
from ml.data_generator.seasonality import SeasonalityEngine
from ml.data_generator.utils import month_dates
from ml.data_generator.weather_generator import WeatherEngine


class SyntheticDatasetGenerator:
    """Orchestrates reproducible enterprise-month synthetic data generation."""

    def __init__(self, config: GeneratorConfig | None = None) -> None:
        self.config = config or GeneratorConfig()
        self.rng = np.random.default_rng(self.config.seed)
        self.enterprise_generator = EnterpriseGenerator(self.config, self.rng)
        self.seasonality_engine = SeasonalityEngine(self.rng)
        self.weather_engine = WeatherEngine(self.rng, self.config.noise_std)
        self.commodity_engine = CommodityEngine(self.rng, self.config.noise_std)
        self.loan_engine = LoanEngine(self.rng)
        self.finance_engine = FinanceEngine(
            self.rng, self.loan_engine, self.config.noise_std
        )
        self.risk_engine = RiskEngine()

    def generate(self) -> pd.DataFrame:
        enterprises = self.enterprise_generator.generate_all()
        records: list[dict[str, Any]] = []
        dates = month_dates(self.config.start_date, self.config.generation_months)
        for enterprise in enterprises:
            records.extend(self._generate_enterprise_records(enterprise, dates))
        frame = pd.DataFrame(records)
        frame = self._add_history_and_targets(frame)
        return self._apply_data_quality(frame)

    def generate_and_export(self) -> tuple[pd.DataFrame, dict[str, Path]]:
        frame = self.generate()
        exported = export_dataset(frame, self.config)
        if self.config.generate_report:
            generate_analysis_report(frame, self.config)
        return frame, exported

    def _generate_enterprise_records(
        self, enterprise: EnterpriseContext, dates: Iterable[date]
    ) -> list[dict[str, Any]]:
        profile = SECTOR_PROFILES[enterprise.sector]
        finance_state = self.finance_engine.initialize_state(enterprise)
        loan_state = self.loan_engine.initialize(
            profile, enterprise.base_monthly_income
        )
        rows: list[dict[str, Any]] = []
        for month_index, month_date in enumerate(dates):
            seasonal = self.seasonality_engine.context(
                month_date.month, enterprise.sector
            )
            weather = self.weather_engine.generate(
                enterprise.location, month_date.month, seasonal
            )
            commodities = self.commodity_engine.generate(
                enterprise.location,
                month_date.month,
                seasonal,
                profile.commodity_exposure,
            )
            finance = self.finance_engine.generate_month(
                enterprise,
                profile,
                finance_state,
                loan_state,
                month_index,
                seasonal,
                weather,
                commodities,
            )
            risk = self.risk_engine.generate(
                finance,
                weather,
                seasonal,
                enterprise.base_monthly_income,
            )
            rows.append(
                self._compose_row(
                    enterprise,
                    month_date,
                    seasonal,
                    weather,
                    commodities,
                    finance,
                    risk,
                    loan_state,
                )
            )
        return rows

    @staticmethod
    def _compose_row(
        enterprise: EnterpriseContext,
        month_date: date,
        seasonal: Any,
        weather: Any,
        commodities: Any,
        finance: FinanceSnapshot,
        risk: Any,
        loan: LoanState,
    ) -> dict[str, Any]:
        return {
            "enterprise_id": enterprise.enterprise_id,
            "enterprise_code": enterprise.enterprise_code,
            "enterprise_name": enterprise.enterprise_name,
            "owner_name": enterprise.owner_name,
            "sector": enterprise.sector,
            "enterprise_type": enterprise.enterprise_type,
            "state": enterprise.location.state,
            "district": enterprise.location.district,
            "village": enterprise.location.villages[0],
            "business_start_date": enterprise.business_start_date,
            "employees": enterprise.employees,
            "annual_turnover": enterprise.annual_turnover,
            "month_date": month_date,
            "month": month_date.month,
            "year": month_date.year,
            "season": seasonal.season,
            "festival_demand_factor": seasonal.festival_demand_factor,
            "harvest_factor": seasonal.harvest_factor,
            "monsoon_factor": seasonal.monsoon_factor,
            "summer_factor": seasonal.summer_factor,
            "seasonal_income_factor": seasonal.seasonal_income_factor,
            "seasonal_expense_factor": seasonal.seasonal_expense_factor,
            "market_event": seasonal.market_event,
            "event_income_factor": seasonal.event_income_factor,
            "event_expense_factor": seasonal.event_expense_factor,
            "supply_chain_delay_days": seasonal.supply_chain_delay_days,
            "market_price_multiplier": seasonal.commodity_price_multiplier,
            "temperature": weather.temperature,
            "rainfall": weather.rainfall,
            "humidity": weather.humidity,
            "weather_condition": weather.condition,
            "weather_shock_index": weather.shock_index,
            "milk_price": commodities.prices["milk"],
            "feed_price": commodities.prices["feed"],
            "grains_price": commodities.prices["grains"],
            "vegetables_price": commodities.prices["vegetables"],
            "fish_feed_price": commodities.prices["fish_feed"],
            "fuel_price": commodities.prices["fuel"],
            "electricity_price": commodities.prices["electricity"],
            "commodity_price_pressure": commodities.price_pressure,
            "income": finance.income,
            "expense": finance.expense,
            "profit": finance.profit,
            "savings": finance.savings,
            "cash_balance": finance.cash_balance,
            "inventory_value": finance.inventory_value,
            "upi_transaction_count": finance.upi_transaction_count,
            "upi_inflow": finance.upi_inflow,
            "upi_outflow": finance.upi_outflow,
            "net_cash_flow": finance.net_cash_flow,
            "loan_type": loan.loan_type,
            "principal_amount": loan.principal_amount,
            "interest_rate": loan.interest_rate,
            "monthly_installment": finance.loan_installment,
            "outstanding_loan": finance.outstanding_loan,
            "loan_payment_status": finance.loan_payment_status,
            "loan_late_payment_probability": finance.loan_late_payment_probability,
            "loan_default_flag": finance.loan_default_flag,
            "debt_service_ratio": finance.debt_service_ratio,
            "risk_score": risk.risk_score,
            "risk_level": risk.risk_level,
            "negative_cash_flow_flag": risk.negative_cash_flow_flag,
            "low_savings_flag": risk.low_savings_flag,
            "high_debt_flag": risk.high_debt_flag,
            "weather_shock_flag": risk.weather_shock_flag,
            "risk_factors": risk.risk_factors,
        }

    def _add_history_and_targets(self, frame: pd.DataFrame) -> pd.DataFrame:
        frame = frame.sort_values(["enterprise_id", "month_date"]).reset_index(
            drop=True
        )
        grouped = frame.groupby("enterprise_id", sort=False)
        frame["income_lag_1"] = grouped["income"].shift(1)
        frame["income_lag_3"] = grouped["income"].shift(3)
        frame["expense_lag_1"] = grouped["expense"].shift(1)
        frame["cash_balance_lag_1"] = grouped["cash_balance"].shift(1)
        frame["profit_lag_1"] = grouped["profit"].shift(1)
        frame["income_rolling_3m"] = grouped["income"].transform(
            lambda values: values.rolling(3, min_periods=1).mean()
        )
        frame["expense_rolling_3m"] = grouped["expense"].transform(
            lambda values: values.rolling(3, min_periods=1).mean()
        )
        frame["cash_flow_volatility_3m"] = grouped["net_cash_flow"].transform(
            lambda values: values.rolling(3, min_periods=1).std(ddof=0)
        )
        frame["revenue_growth_3m"] = grouped["income"].transform(
            lambda values: values.pct_change(3).replace([np.inf, -np.inf], 0.0)
        )
        lag_fallbacks = {
            "income_lag_1": "income",
            "income_lag_3": "income",
            "expense_lag_1": "expense",
            "cash_balance_lag_1": "cash_balance",
            "profit_lag_1": "profit",
        }
        for target_column, fallback_column in lag_fallbacks.items():
            frame[target_column] = frame[target_column].fillna(frame[fallback_column])
        frame["revenue_growth_3m"] = frame["revenue_growth_3m"].fillna(0.0)

        history_mask = (
            frame.groupby("enterprise_id").cumcount() < self.config.history_months
        )
        history = frame.loc[history_mask].copy()
        for horizon in self.config.target_horizons:
            target = frame.groupby("enterprise_id")["net_cash_flow"].shift(-horizon)
            history[f"cash_flow_after_{horizon}_month"] = target.loc[
                history.index
            ].to_numpy()
        return history.reset_index(drop=True)

    def _apply_data_quality(self, frame: pd.DataFrame) -> pd.DataFrame:
        if self.config.outlier_rate > 0:
            numeric_columns = [
                column
                for column in frame.select_dtypes(include=[np.number]).columns
                if column in self.config.outlier_columns
            ]
            for column in numeric_columns:
                mask = self.rng.random(len(frame)) < self.config.outlier_rate
                factors = self.rng.choice((0.35, 2.25), size=int(mask.sum()))
                frame.loc[mask, column] = frame.loc[mask, column].to_numpy() * factors

        if self.config.missing_data_rate > 0:
            protected = {
                "enterprise_id",
                "enterprise_code",
                "month_date",
                "month",
                "year",
            }
            feature_columns = [
                column
                for column in frame.columns
                if column not in protected and "after_" not in column
            ]
            for column in feature_columns:
                mask = self.rng.random(len(frame)) < self.config.missing_data_rate
                frame.loc[mask, column] = np.nan
        return frame


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate synthetic GramNadi AI datasets."
    )
    parser.add_argument("--enterprises", type=int, default=1000)
    parser.add_argument("--months", type=int, default=36)
    parser.add_argument(
        "--start-date", type=date.fromisoformat, default=date(2023, 1, 1)
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--noise-std", type=float, default=0.04)
    parser.add_argument("--outlier-rate", type=float, default=0.005)
    parser.add_argument("--missing-data-rate", type=float, default=0.0)
    parser.add_argument("--output-dir", type=Path, default=Path("datasets"))
    parser.add_argument("--formats", nargs="+", default=["csv", "parquet", "json"])
    parser.add_argument("--no-report", action="store_true")
    return parser


def main() -> None:
    args = _build_parser().parse_args()
    config = GeneratorConfig(
        enterprise_count=args.enterprises,
        history_months=args.months,
        start_date=args.start_date,
        seed=args.seed,
        noise_std=args.noise_std,
        outlier_rate=args.outlier_rate,
        missing_data_rate=args.missing_data_rate,
        output_dir=args.output_dir,
        export_formats=tuple(args.formats),
        generate_report=not args.no_report,
    )
    frame, exports = SyntheticDatasetGenerator(config).generate_and_export()
    print(f"Generated {len(frame):,} enterprise-month rows.")
    for format_name, path in exports.items():
        print(f"{format_name}: {path}")
    if config.generate_report:
        print(f"report: {config.output_dir / 'reports'}")


if __name__ == "__main__":
    main()
