from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import numpy as np

from ml.data_generator.config import (
    LOCATION_PROFILES,
    SECTOR_NAMES,
    SECTOR_PROFILES,
    GeneratorConfig,
    LocationProfile,
)
from ml.data_generator.utils import choose_weighted


@dataclass(frozen=True)
class EnterpriseContext:
    enterprise_id: str
    enterprise_code: str
    enterprise_name: str
    owner_name: str
    sector: str
    enterprise_type: str
    location: LocationProfile
    business_start_date: date
    employees: int
    annual_turnover: float
    base_monthly_income: float
    initial_cash_balance: float
    initial_inventory_value: float
    initial_savings: float


class EnterpriseGenerator:
    """Creates stable enterprise profiles that seed each monthly simulation."""

    _OWNER_NAMES = (
        "Asha Patil",
        "Ramesh Yadav",
        "Meena Das",
        "Suresh Gowda",
        "Lakshmi Nair",
        "Vijay Shah",
        "Kavita Singh",
        "Mohan Pradhan",
        "Farida Sheikh",
        "Anil Kumawat",
        "Sunita Devi",
        "Bharat Naik",
    )

    def __init__(self, config: GeneratorConfig, rng: np.random.Generator) -> None:
        self.config = config
        self.rng = rng

    def generate_all(self) -> list[EnterpriseContext]:
        sector_weights = [
            self.config.sector_weights.get(sector, 0.0) for sector in SECTOR_NAMES
        ]
        enterprises: list[EnterpriseContext] = []
        for index in range(self.config.enterprise_count):
            sector = choose_weighted(self.rng, SECTOR_NAMES, sector_weights)
            profile = SECTOR_PROFILES[sector]
            location = LOCATION_PROFILES[
                int(self.rng.integers(0, len(LOCATION_PROFILES)))
            ]
            enterprise_number = index + 1
            employees = int(
                self.rng.integers(profile.employees_low, profile.employees_high + 1)
            )
            base_income = profile.base_monthly_income * float(
                self.rng.lognormal(0.0, 0.10)
            )
            start_date = date(
                int(self.rng.integers(2012, 2021)),
                int(self.rng.integers(1, 13)),
                1,
            )
            years_active = max(1.0, (self.config.start_date - start_date).days / 365.25)
            annual_turnover = base_income * 12.0 * min(1.35, 1.0 + years_active * 0.025)
            initial_cash = base_income * float(self.rng.uniform(1.0, 3.2))
            initial_inventory = base_income * profile.inventory_days / 30.0
            initial_savings = base_income * float(self.rng.uniform(0.20, 0.90))
            village = location.villages[
                int(self.rng.integers(0, len(location.villages)))
            ]
            enterprises.append(
                EnterpriseContext(
                    enterprise_id=f"enterprise-{enterprise_number:06d}",
                    enterprise_code=(
                        f"ENT-{location.state[:2].upper()}-{enterprise_number:06d}"
                    ),
                    enterprise_name=f"{sector} Enterprise {enterprise_number:04d}",
                    owner_name=str(self.rng.choice(self._OWNER_NAMES)),
                    sector=sector,
                    enterprise_type=profile.enterprise_type,
                    location=LocationProfile(
                        state=location.state,
                        district=location.district,
                        villages=(village,),
                        climate_zone=location.climate_zone,
                        mean_temperature_c=location.mean_temperature_c,
                        temperature_amplitude_c=location.temperature_amplitude_c,
                        monsoon_months=location.monsoon_months,
                        monsoon_rainfall_mm=location.monsoon_rainfall_mm,
                        dry_rainfall_mm=location.dry_rainfall_mm,
                        humidity_base=location.humidity_base,
                    ),
                    business_start_date=start_date,
                    employees=employees,
                    annual_turnover=round(annual_turnover, 2),
                    base_monthly_income=round(base_income, 2),
                    initial_cash_balance=round(initial_cash, 2),
                    initial_inventory_value=round(initial_inventory, 2),
                    initial_savings=round(initial_savings, 2),
                )
            )
        return enterprises
