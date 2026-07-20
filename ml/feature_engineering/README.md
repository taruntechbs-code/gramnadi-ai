# GramNadi AI Phase 3A: Feature Engineering

This package converts the Phase 2 synthetic rural-enterprise dataset into
validated, chronologically split, ML-ready feature tables. It is deliberately
limited to data preparation: it does not train models, expose inference APIs,
or modify the backend, frontend, database schema, or Phase 2 generator.

## Run the pipeline

From the repository root:

```bash
backend/.venv/bin/python -m ml.feature_engineering
```

The default run reads
`datasets/synthetic_rural_financial_data.parquet`, writes processed data to
`ml/processed/`, and writes reports to `ml/feature_engineering/reports/`.
The CLI also accepts CSV input and configurable output locations:

```bash
backend/.venv/bin/python -m ml.feature_engineering \
  --input datasets/synthetic_rural_financial_data.csv \
  --input-format csv \
  --scaling standard \
  --output-dir ml/processed \
  --reports-dir ml/feature_engineering/reports
```

Supported scaling methods are `none` (the default), `standard`, `minmax`, and
`robust`. Encoders and scalers are fitted on the training partition only and
then applied to validation and test data. The chronological split is 70% / 15%
/ 15% by unique month, with no shuffling; for the default 36-month, 1,000-
enterprise dataset this produces 25,000 / 5,000 / 6,000 rows.

## Pipeline stages

1. Load CSV or Parquet and normalize date columns.
2. Validate schema, chronology, enterprise continuity, value ranges,
   duplicates, and target leakage candidates.
3. Profile dimensions, dtypes, missingness, distributions, and correlations.
4. Build time, financial, weather, commodity, enterprise-history, lag,
   rolling, and interaction features.
5. Assess constants, near-zero variance, redundancy, correlation, and leakage.
6. Fit missing-value handling and one-hot encoding on training data.
7. Optionally fit a numeric scaler on training data.
8. Export split datasets, metadata, reusable preprocessing artifacts, and
   reports.

## Outputs

`ml/processed/` contains `train.csv`, `validation.csv`, and `test.csv`, their
Parquet equivalents, `feature_metadata.json`, `encoder.pkl`, and
`pipeline_artifact.joblib`. `scaler.pkl` is created only when scaling is
enabled.

`ml/feature_engineering/reports/` contains validation, profiling, feature
quality, processing summary, configuration, encoding/scaler metadata,
correlation CSV/PNG files, feature-distribution plots, and a processing log.

The Phase 2 generator remains the source of truth for dataset creation and is
run independently. Reproducibility is controlled by the configured seed and
the immutable input dataset; the feature pipeline itself performs no random
sampling.

## Development checks

```bash
backend/.venv/bin/isort ml/feature_engineering
backend/.venv/bin/black ml/feature_engineering
backend/.venv/bin/flake8 ml/feature_engineering
```

On the default local environment, the 36,000-row dataset completes the full
pipeline in roughly 7 seconds of Python runtime, excluding shell startup and
filesystem variance.
