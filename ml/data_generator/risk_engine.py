from __future__ import annotations

from dataclasses import dataclass

from ml.data_generator.finance_generator import FinanceSnapshot
from ml.data_generator.seasonality import SeasonalContext
from ml.data_generator.utils import clamp, safe_divide
from ml.data_generator.weather_generator import WeatherSnapshot


@dataclass(frozen=True)
class RiskSnapshot:
    risk_score: float
    risk_level: str
    negative_cash_flow_flag: int
    low_savings_flag: int
    high_debt_flag: int
    weather_shock_flag: int
    risk_factors: str


class RiskEngine:
    """Creates explainable ground-truth risk labels from observable conditions."""

    def generate(
        self,
        finance: FinanceSnapshot,
        weather: WeatherSnapshot,
        seasonal: SeasonalContext,
        initial_income: float,
    ) -> RiskSnapshot:
        factors: list[str] = []
        score = 8.0
        if finance.net_cash_flow < 0:
            score += 30.0
            factors.append("negative_cash_flow")
        if finance.savings < initial_income * 0.04:
            score += 18.0
            factors.append("low_monthly_savings")
        debt_ratio = finance.debt_service_ratio
        if debt_ratio > 0.25:
            score += 20.0
            factors.append("high_debt_service")
        elif debt_ratio > 0.15:
            score += 9.0
            factors.append("elevated_debt_service")
        if finance.outstanding_loan > initial_income * 8:
            score += 12.0
            factors.append("high_outstanding_loan")
        if weather.shock_index >= 0.45:
            score += 15.0
            factors.append("weather_shock")
        if seasonal.market_event not in {"none", "festival_demand_surge"}:
            score += 8.0
            factors.append(seasonal.market_event)
        if finance.loan_default_flag:
            score += 16.0
            factors.append("loan_default")
        if finance.cash_balance < 0:
            score += 12.0
            factors.append("negative_cash_balance")

        volatility_penalty = clamp(
            safe_divide(abs(finance.profit), max(finance.income, 1.0), default=0.0) * 4,
            0.0,
            4.0,
        )
        score = clamp(score + volatility_penalty, 0.0, 100.0)
        if score < 35:
            level = "low"
        elif score < 65:
            level = "medium"
        else:
            level = "high"
        return RiskSnapshot(
            risk_score=round(score, 2),
            risk_level=level,
            negative_cash_flow_flag=int(finance.net_cash_flow < 0),
            low_savings_flag=int(finance.savings < initial_income * 0.04),
            high_debt_flag=int(debt_ratio > 0.25),
            weather_shock_flag=int(weather.shock_index >= 0.45),
            risk_factors="|".join(dict.fromkeys(factors)) or "none",
        )
