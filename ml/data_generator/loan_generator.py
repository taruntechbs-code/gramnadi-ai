from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ml.data_generator.config import SectorProfile
from ml.data_generator.utils import clamp, safe_divide


@dataclass
class LoanState:
    loan_type: str
    principal_amount: float
    interest_rate: float
    monthly_installment: float
    outstanding_loan: float
    late_payment_probability: float
    payment_status: str
    default_flag: int


class LoanEngine:
    """Creates and amortizes one representative enterprise loan portfolio."""

    _LOAN_TERMS = {
        "crop_loan": (0.105, 24),
        "working_capital": (0.135, 36),
        "equipment_loan": (0.115, 48),
        "shg_loan": (0.12, 30),
    }

    def __init__(self, rng: np.random.Generator) -> None:
        self.rng = rng

    def initialize(self, profile: SectorProfile, base_income: float) -> LoanState:
        if float(self.rng.random()) > profile.loan_probability:
            return LoanState("none", 0.0, 0.0, 0.0, 0.0, 0.0, "no_loan", 0)
        loan_type = str(self.rng.choice(profile.preferred_loan_types))
        annual_rate, term_months = self._LOAN_TERMS[loan_type]
        principal = base_income * float(self.rng.uniform(2.0, 7.0))
        monthly_rate = annual_rate / 12.0
        installment = (
            principal
            * monthly_rate
            * (1 + monthly_rate) ** term_months
            / ((1 + monthly_rate) ** term_months - 1)
        )
        return LoanState(
            loan_type=loan_type,
            principal_amount=round(principal, 2),
            interest_rate=round(annual_rate * 100, 2),
            monthly_installment=round(installment, 2),
            outstanding_loan=round(principal, 2),
            late_payment_probability=0.03,
            payment_status="current",
            default_flag=0,
        )

    def monthly_update(
        self,
        state: LoanState,
        income: float,
        expense: float,
        cash_balance: float,
        weather_shock: float,
        event: str,
    ) -> LoanState:
        if state.loan_type == "none" or state.outstanding_loan <= 0:
            state.outstanding_loan = 0.0
            state.payment_status = "no_loan"
            return state

        stress = clamp(
            safe_divide(
                expense - max(cash_balance, 0.0), max(income, 1.0), default=0.0
            ),
            0.0,
            1.0,
        )
        event_stress = (
            0.15 if event in {"flood", "drought", "disease_outbreak"} else 0.0
        )
        state.late_payment_probability = round(
            clamp(
                0.03 + stress * 0.32 + weather_shock * 0.22 + event_stress, 0.01, 0.85
            ),
            4,
        )
        late = float(self.rng.random()) < state.late_payment_probability
        interest_due = state.outstanding_loan * (state.interest_rate / 100.0) / 12.0
        if late:
            paid = state.monthly_installment * float(self.rng.uniform(0.0, 0.55))
            state.payment_status = "late"
        else:
            paid = state.monthly_installment
            state.payment_status = "paid"
        principal_paid = max(0.0, paid - interest_due)
        state.outstanding_loan = round(
            max(
                0.0,
                state.outstanding_loan
                - principal_paid
                + (interest_due if late else 0.0),
            ),
            2,
        )
        if state.outstanding_loan > state.principal_amount * 1.08 or (
            state.payment_status == "late" and stress > 0.82
        ):
            state.default_flag = 1
            state.payment_status = "defaulted"
        return state
