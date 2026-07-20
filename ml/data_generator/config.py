from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Final


@dataclass(frozen=True)
class LocationProfile:
    state: str
    district: str
    villages: tuple[str, ...]
    climate_zone: str
    mean_temperature_c: float
    temperature_amplitude_c: float
    monsoon_months: tuple[int, ...]
    monsoon_rainfall_mm: float
    dry_rainfall_mm: float
    humidity_base: float


@dataclass(frozen=True)
class SectorProfile:
    name: str
    enterprise_type: str
    base_monthly_income: float
    expense_ratio: float
    fixed_monthly_cost: float
    monthly_growth_rate: float
    income_volatility: float
    input_cost_sensitivity: float
    weather_sensitivity: float
    inventory_days: int
    employees_low: int
    employees_high: int
    loan_probability: float
    savings_rate: float
    upi_share: float
    average_transaction_value: float
    preferred_loan_types: tuple[str, ...]
    commodity_exposure: tuple[str, ...]


@dataclass(frozen=True)
class EventProfile:
    name: str
    probability: float
    income_multiplier: float
    expense_multiplier: float
    weather_shock: float
    supply_chain_delay_days: int
    commodity_price_multiplier: float


SECTOR_NAMES: Final[tuple[str, ...]] = (
    "Dairy",
    "Poultry",
    "Handicrafts",
    "Food Processing",
    "Rural Retail",
    "Fisheries",
    "Agriculture",
    "Weaving",
    "Goat Farming",
    "Beekeeping",
)

LOCATION_PROFILES: Final[tuple[LocationProfile, ...]] = (
    LocationProfile(
        "Maharashtra",
        "Pune",
        ("Khed", "Baramati", "Junnar", "Mulshi"),
        "tropical_wet_dry",
        25.0,
        7.5,
        (6, 7, 8, 9),
        180.0,
        12.0,
        62.0,
    ),
    LocationProfile(
        "Uttar Pradesh",
        "Lucknow",
        ("Malihabad", "Mohan", "Bakshi Ka Talab", "Mohanlalganj"),
        "subtropical",
        25.5,
        10.5,
        (6, 7, 8, 9),
        160.0,
        8.0,
        58.0,
    ),
    LocationProfile(
        "Tamil Nadu",
        "Madurai",
        ("Melur", "Usilampatti", "Thirumangalam", "Perungudi"),
        "semi_arid",
        28.0,
        5.5,
        (10, 11, 12),
        130.0,
        18.0,
        60.0,
    ),
    LocationProfile(
        "Karnataka",
        "Mysuru",
        ("Nanjangud", "Hunsur", "Tirumakudalu", "Periyapatna"),
        "tropical_savanna",
        24.5,
        6.0,
        (6, 7, 8, 9),
        145.0,
        14.0,
        65.0,
    ),
    LocationProfile(
        "West Bengal",
        "Nadia",
        ("Krishnanagar", "Ranaghat", "Tehatta", "Chakdaha"),
        "humid_subtropical",
        26.0,
        8.0,
        (6, 7, 8, 9),
        220.0,
        15.0,
        72.0,
    ),
    LocationProfile(
        "Odisha",
        "Ganjam",
        ("Berhampur", "Chhatrapur", "Aska", "Polasara"),
        "coastal_tropical",
        27.0,
        5.5,
        (6, 7, 8, 9, 10),
        240.0,
        20.0,
        74.0,
    ),
    LocationProfile(
        "Gujarat",
        "Anand",
        ("Borsad", "Petlad", "Khambhat", "Sojitra"),
        "semi_arid",
        27.0,
        8.5,
        (6, 7, 8, 9),
        115.0,
        7.0,
        56.0,
    ),
    LocationProfile(
        "Kerala",
        "Alappuzha",
        ("Kuttanad", "Cherthala", "Ambalappuzha", "Haripad"),
        "humid_tropical",
        27.0,
        3.0,
        (5, 6, 7, 8, 9, 10),
        310.0,
        38.0,
        80.0,
    ),
)

SECTOR_PROFILES: Final[dict[str, SectorProfile]] = {
    "Dairy": SectorProfile(
        "Dairy",
        "livestock",
        92000,
        0.69,
        9000,
        0.003,
        0.06,
        0.42,
        0.34,
        8,
        2,
        8,
        0.72,
        0.22,
        0.78,
        620,
        ("working_capital", "equipment_loan"),
        ("feed", "fuel", "electricity"),
    ),
    "Poultry": SectorProfile(
        "Poultry",
        "livestock",
        125000,
        0.78,
        12000,
        0.004,
        0.13,
        0.58,
        0.45,
        7,
        2,
        12,
        0.78,
        0.18,
        0.82,
        760,
        ("working_capital", "equipment_loan"),
        ("feed", "fuel", "electricity"),
    ),
    "Handicrafts": SectorProfile(
        "Handicrafts",
        "handicraft",
        58000,
        0.51,
        5000,
        0.002,
        0.20,
        0.18,
        0.12,
        45,
        1,
        10,
        0.42,
        0.30,
        0.55,
        850,
        ("shg_loan", "working_capital"),
        ("fuel", "electricity"),
    ),
    "Food Processing": SectorProfile(
        "Food Processing",
        "food_processing",
        145000,
        0.67,
        15000,
        0.004,
        0.10,
        0.38,
        0.20,
        20,
        3,
        18,
        0.76,
        0.24,
        0.78,
        980,
        ("working_capital", "equipment_loan"),
        ("grains", "vegetables", "fuel", "electricity"),
    ),
    "Rural Retail": SectorProfile(
        "Rural Retail",
        "retail",
        110000,
        0.84,
        11000,
        0.003,
        0.08,
        0.28,
        0.16,
        30,
        1,
        8,
        0.61,
        0.15,
        0.88,
        540,
        ("working_capital", "shg_loan"),
        ("grains", "vegetables", "fuel", "electricity"),
    ),
    "Fisheries": SectorProfile(
        "Fisheries",
        "fisheries",
        135000,
        0.66,
        13000,
        0.004,
        0.18,
        0.46,
        0.58,
        12,
        2,
        12,
        0.69,
        0.20,
        0.74,
        880,
        ("crop_loan", "equipment_loan"),
        ("fish_feed", "fuel", "electricity"),
    ),
    "Agriculture": SectorProfile(
        "Agriculture",
        "agriculture",
        98000,
        0.55,
        8000,
        0.003,
        0.24,
        0.36,
        0.72,
        55,
        1,
        12,
        0.82,
        0.24,
        0.64,
        760,
        ("crop_loan", "working_capital"),
        ("grains", "vegetables", "fuel", "electricity"),
    ),
    "Weaving": SectorProfile(
        "Weaving",
        "manufacturing",
        76000,
        0.58,
        7000,
        0.003,
        0.16,
        0.27,
        0.10,
        30,
        2,
        14,
        0.58,
        0.26,
        0.66,
        680,
        ("equipment_loan", "shg_loan"),
        ("fuel", "electricity"),
    ),
    "Goat Farming": SectorProfile(
        "Goat Farming",
        "livestock",
        69000,
        0.53,
        6000,
        0.003,
        0.19,
        0.30,
        0.44,
        20,
        1,
        8,
        0.64,
        0.25,
        0.58,
        720,
        ("crop_loan", "shg_loan"),
        ("feed", "fuel"),
    ),
    "Beekeeping": SectorProfile(
        "Beekeeping",
        "agriculture",
        63000,
        0.47,
        4500,
        0.003,
        0.23,
        0.19,
        0.52,
        25,
        1,
        6,
        0.48,
        0.28,
        0.60,
        640,
        ("shg_loan", "working_capital"),
        ("fuel", "electricity"),
    ),
}

EVENT_PROFILES: Final[tuple[EventProfile, ...]] = (
    EventProfile("flood", 0.018, 0.72, 1.28, 0.85, 18, 1.12),
    EventProfile("drought", 0.022, 0.78, 1.12, 0.72, 10, 1.08),
    EventProfile("heavy_rain", 0.035, 0.90, 1.08, 0.48, 7, 1.04),
    EventProfile("disease_outbreak", 0.018, 0.76, 1.24, 0.62, 2, 1.03),
    EventProfile("supply_chain_delay", 0.045, 0.91, 1.13, 0.18, 12, 1.08),
    EventProfile("fuel_price_increase", 0.030, 0.98, 1.14, 0.08, 3, 1.06),
    EventProfile("market_price_crash", 0.022, 0.83, 1.00, 0.15, 0, 0.76),
    EventProfile("festival_demand_surge", 0.040, 1.24, 1.08, 0.0, 0, 1.02),
)


@dataclass(frozen=True)
class GeneratorConfig:
    enterprise_count: int = 1000
    history_months: int = 36
    start_date: date = date(2023, 1, 1)
    seed: int = 42
    noise_std: float = 0.04
    outlier_rate: float = 0.005
    missing_data_rate: float = 0.0
    output_dir: Path = Path("datasets")
    export_formats: tuple[str, ...] = ("csv", "parquet", "json")
    target_horizons: tuple[int, ...] = (1, 3, 6)
    generate_report: bool = True
    report_sample_size: int = 100_000
    outlier_columns: tuple[str, ...] = (
        "annual_turnover",
        "rainfall",
        "milk_price",
        "feed_price",
        "grains_price",
        "vegetables_price",
        "fish_feed_price",
        "fuel_price",
        "electricity_price",
    )
    sector_weights: dict[str, float] = field(
        default_factory=lambda: {sector: 1.0 for sector in SECTOR_NAMES}
    )

    def __post_init__(self) -> None:
        if self.enterprise_count <= 0:
            raise ValueError("enterprise_count must be positive")
        if self.history_months < max(self.target_horizons, default=0) + 1:
            raise ValueError("history_months must leave room for every target horizon")
        if self.noise_std < 0:
            raise ValueError("noise_std cannot be negative")
        for name, value in (
            ("outlier_rate", self.outlier_rate),
            ("missing_data_rate", self.missing_data_rate),
        ):
            if not 0 <= value < 1:
                raise ValueError(f"{name} must be between 0 and 1")
        if not self.target_horizons or any(
            horizon <= 0 for horizon in self.target_horizons
        ):
            raise ValueError("target_horizons must contain positive values")
        if not self.export_formats:
            raise ValueError("at least one export format is required")
        unsupported = set(self.export_formats) - {"csv", "parquet", "json"}
        if unsupported:
            raise ValueError(f"unsupported export formats: {sorted(unsupported)}")

    @property
    def generation_months(self) -> int:
        return self.history_months + max(self.target_horizons)
