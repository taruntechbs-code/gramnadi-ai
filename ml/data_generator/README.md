# GramNadi AI synthetic data generator

This package generates deterministic, explainable monthly panel data for rural micro enterprises. It is designed for future cash-flow forecasting, financial-risk modelling, explainability, and counterfactual simulation work. It does not train models, call model APIs, calculate predictions, or modify the backend schema.

## Quick start

From the repository root:

```bash
python3 -m pip install -r ml/data_generator/requirements.txt
python3 -m ml.data_generator --enterprises 1000 --months 36 --seed 42
```

The command writes:

- `datasets/synthetic_rural_financial_data.csv`
- `datasets/synthetic_rural_financial_data.parquet`
- `datasets/synthetic_rural_financial_data.json`
- `datasets/reports/feature_distributions.png`
- `datasets/reports/sector_counts.png`
- `datasets/reports/risk_distribution.png`
- `datasets/reports/cash_flow_distribution.png`
- `datasets/reports/correlation_matrix.png`
- `datasets/reports/summary.json`

For a fast local smoke run without plotting:

```bash
python3 -m ml.data_generator --enterprises 100 --months 12 --formats csv --no-report
```

Supported recommended enterprise counts are 100, 500, 1,000, 5,000, and 10,000. The engine also accepts other positive values for tests and experiments.

## Generation pipeline

1. `EnterpriseGenerator` creates a stable enterprise profile: sector, enterprise type, owner, Indian location, employees, business age, turnover, starting cash, inventory, and savings.
2. `SeasonalityEngine` applies winter, summer, monsoon, post-monsoon, harvest, festival, and market-event effects.
3. `WeatherEngine` produces district-sensitive temperature, rainfall, humidity, condition, and a bounded weather-shock index.
4. `CommodityEngine` produces correlated monthly prices for milk, feed, grains, vegetables, fish feed, fuel, and electricity.
5. `LoanEngine` initializes a sector-appropriate loan and amortizes outstanding principal, interest, payment status, late-payment probability, and default flags.
6. `FinanceEngine` derives income, expenses, profit, savings, cash balance, inventory, UPI activity, loan installment, and net cash flow from the prior state and current context.
7. `RiskEngine` produces rule-based ground-truth risk labels and a pipe-delimited explanation of the contributing factors.
8. The orchestrator adds lagged, rolling, volatility, growth, and 1/3/6-month future cash-flow target columns.
9. The export layer writes tabular files and an analysis report.

The engine internally simulates six additional months when 1-, 3-, and 6-month targets are requested. Only the configured history window is exported, so every exported history row has a complete future target.

## Business assumptions

- Income is sector-specific, grows gradually, and responds to seasonality, inventory availability, weather, supply-chain delay, events, and controlled noise.
- Expenses are a function of income, fixed operating costs, seasonal costs, commodity pressure, weather stress, and events.
- Profit is `income - expense`; net cash flow is `profit - loan installment`.
- Inventory is a smoothed operating stock and affects the following month’s sales capacity.
- UPI inflow is a sector-specific share of income; UPI outflow is a bounded share of expense.
- Loans are amortizing, with sector-specific loan-type preferences and stress-sensitive late-payment probability.
- Cash balance is allowed to become negative so liquidity distress is observable rather than hidden by clipping.
- Risk is a ground-truth label generated from negative cash flow, low savings, debt service, loan balance, weather shocks, events, defaults, and cash deficits.

## Sector logic

The ten supported sectors are Dairy, Poultry, Handicrafts, Food Processing, Rural Retail, Fisheries, Agriculture, Weaving, Goat Farming, and Beekeeping. Each profile controls baseline income, expense ratio, fixed costs, growth, volatility, input-cost sensitivity, weather sensitivity, inventory days, staffing, loan likelihood, savings behavior, UPI adoption, transaction size, loan types, and commodity exposure.

## Weather and commodity logic

District profiles encode state, district, village names, climate zone, temperature range, monsoon months, rainfall expectations, and humidity. Weather conditions are derived from generated rainfall and temperature, while drought, flood, and heavy-rain events alter the climate signal. Commodity prices have sector-neutral base prices and monthly seasonal curves; market events apply explicit price multipliers. District variation is deterministic and seed-controlled.

## Risk and target logic

Risk scores are bounded from 0 to 100 and labelled `low`, `medium`, or `high`. The `risk_factors` column makes the rule-based label inspectable. The future target columns are shifted realized synthetic net cash flows:

- `cash_flow_after_1_month`
- `cash_flow_after_3_month`
- `cash_flow_after_6_month`

They are targets for future modelling, not predictions made by this package.

## Data quality controls

`GeneratorConfig` controls seed, noise, outlier rate, missing-data rate, history length, target horizons, formats, output location, report sample size, and sector weights. By default, identifiers and target columns are complete and `missing_data_rate=0`, so the generated dataset contains no missing values. Configured missingness is applied only to non-identifier, non-target features. Outliers are multiplicative and applied only to numeric feature columns.

## Programmatic usage

```python
from ml.data_generator.config import GeneratorConfig
from ml.data_generator.generator import SyntheticDatasetGenerator

config = GeneratorConfig(
    enterprise_count=500,
    history_months=36,
    seed=7,
    output_dir="datasets/experiment-7",
    export_formats=("parquet",),
    generate_report=False,
)
frame = SyntheticDatasetGenerator(config).generate()
print(frame.shape)
```

The generator is deterministic for the same configuration and seed. All output paths are created with `pathlib`, and export/report code is kept separate from simulation logic.

On the validation machine, the default 1,000-enterprise, 36-month run completed in approximately 3.2 seconds with CSV, Parquet, JSON, and report generation enabled. Runtime varies with hardware and storage speed.
