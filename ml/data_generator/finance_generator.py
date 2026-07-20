from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ml.data_generator.commodity_generator import CommoditySnapshot
from ml.data_generator.config import SectorProfile
from ml.data_generator.enterprise_generator import EnterpriseContext
from ml.data_generator.loan_generator import LoanEngine, LoanState
from ml.data_generator.seasonality import SeasonalContext
from ml.data_generator.utils import clamp, noisy_multiplier, safe_divide
from ml.data_generator.weather_generator import WeatherSnapshot


@dataclass
class FinanceState:
    cash_balance: float
    inventory_value: float
    savings_balance: float
    previous_income: float
    previous_expense: float
    previous_profit: float


@dataclass(frozen=True)
class FinanceSnapshot:
    income: float
    expense: float
    profit: float
    savings: float
    cash_balance: float
    inventory_value: float
    upi_transaction_count: int
    upi_inflow: float
    upi_outflow: float
    loan_installment: float
    outstanding_loan: float
    net_cash_flow: float
    loan_payment_status: str
    loan_default_flag: int
    loan_late_payment_probability: float
    debt_service_ratio: float


class FinanceEngine:
    """Transforms business, climate, market, and loan state into monthly finances."""

    def __init__(
        self,
        rng: np.random.Generator,
        loan_engine: LoanEngine,
        noise_std: float,
    ) -> None:
        self.rng = rng
        self.loan_engine = loan_engine
        self.noise_std = noise_std

    def initialize_state(self, enterprise: EnterpriseContext) -> FinanceState:
        return FinanceState(
            cash_balance=enterprise.initial_cash_balance,
            inventory_value=enterprise.initial_inventory_value,
            savings_balance=enterprise.initial_savings,
            previous_income=enterprise.base_monthly_income,
            previous_expense=enterprise.base_monthly_income * 0.65,
            previous_profit=enterprise.base_monthly_income * 0.12,
        )

    def generate_month(
        self,
        enterprise: EnterpriseContext,
        profile: SectorProfile,
        state: FinanceState,
        loan_state: LoanState,
        month_index: int,
        seasonal: SeasonalContext,
        weather: WeatherSnapshot,
        commodities: CommoditySnapshot,
    ) -> FinanceSnapshot:
        trend_factor = (1.0 + profile.monthly_growth_rate) ** month_index
        weather_factor = 1.0 - profile.weather_sensitivity * weather.shock_index * 0.55
        inventory_target = (
            enterprise.base_monthly_income * profile.inventory_days / 30.0
        )
        inventory_factor = clamp(
            0.82
            + safe_divide(state.inventory_value, max(inventory_target, 1.0)) * 0.18,
            0.70,
            1.10,
        )
        supply_factor = max(0.72, 1.0 - seasonal.supply_chain_delay_days / 100.0)
        income = (
            enterprise.base_monthly_income
            * trend_factor
            * seasonal.seasonal_income_factor
            * seasonal.event_income_factor
            * weather_factor
            * inventory_factor
            * supply_factor
            * noisy_multiplier(self.rng, self.noise_std + profile.income_volatility / 4)
        )
        income = max(100.0, income)

        input_pressure = (
            1.0 + (commodities.price_pressure - 1.0) * profile.input_cost_sensitivity
        )
        weather_expense_factor = (
            1.0 + weather.shock_index * profile.weather_sensitivity * 0.24
        )
        expense = (
            income
            * profile.expense_ratio
            * seasonal.seasonal_expense_factor
            * seasonal.event_expense_factor
            * input_pressure
            * weather_expense_factor
            + profile.fixed_monthly_cost
        )
        expense *= noisy_multiplier(self.rng, self.noise_std / 2)
        expense = max(50.0, expense)

        profit = income - expense
        loan_installment = loan_state.monthly_installment
        net_cash_flow = profit - loan_installment
        savings = max(0.0, profit * profile.savings_rate)
        cash_balance = state.cash_balance + net_cash_flow

        inventory_value = max(
            0.0,
            state.inventory_value * 0.62
            + inventory_target * (commodities.price_pressure**0.35) * 0.38,
        )
        upi_inflow = income * profile.upi_share
        upi_outflow = expense * min(0.92, profile.upi_share * 0.78)
        average_transaction_value = max(profile.average_transaction_value, 1.0)
        upi_transactions = max(
            0,
            int(
                round(
                    upi_inflow
                    / average_transaction_value
                    * noisy_multiplier(self.rng, 0.06)
                )
            ),
        )

        updated_loan = self.loan_engine.monthly_update(
            loan_state,
            income=income,
            expense=expense,
            cash_balance=cash_balance,
            weather_shock=weather.shock_index,
            event=seasonal.market_event,
        )
        debt_service_ratio = safe_divide(loan_installment, income, default=0.0)
        state.cash_balance = cash_balance
        state.inventory_value = inventory_value
        state.savings_balance = state.savings_balance + savings
        state.previous_income = income
        state.previous_expense = expense
        state.previous_profit = profit
        return FinanceSnapshot(
            income=round(income, 2),
            expense=round(expense, 2),
            profit=round(profit, 2),
            savings=round(savings, 2),
            cash_balance=round(cash_balance, 2),
            inventory_value=round(inventory_value, 2),
            upi_transaction_count=upi_transactions,
            upi_inflow=round(upi_inflow, 2),
            upi_outflow=round(upi_outflow, 2),
            loan_installment=round(loan_installment, 2),
            outstanding_loan=round(updated_loan.outstanding_loan, 2),
            net_cash_flow=round(net_cash_flow, 2),
            loan_payment_status=updated_loan.payment_status,
            loan_default_flag=updated_loan.default_flag,
            loan_late_payment_probability=updated_loan.late_payment_probability,
            debt_service_ratio=round(debt_service_ratio, 4),
        )
