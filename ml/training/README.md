# GramNadi AI Phase 3B Training

Phase 3B trains two isolated XGBoost models from the immutable Phase 3A
outputs: a regression model for `future_cashflow_3m` (mapped to Phase 3A's
`cash_flow_after_3_month`) and a classifier for `risk_label` (mapped to
`risk_level`). It does not modify the backend, frontend, database, APIs, or
earlier pipeline phases.

Run from the repository root:

```bash
backend/.venv/bin/python -m ml.training
```

Useful options include `--trials`, `--seed`, `--no-shap`, `--calibration
{auto,platt,isotonic}`, `--input-format {auto,csv,parquet}`, and custom
`--processed-dir`, `--output-dir`, and `--reports-dir` paths. Optuna tuning
uses the validation split only; the test split is held out for final metrics.

Models, metadata, configuration, metrics, and both pickle/joblib artifacts are
written to `ml/models/`. Evaluation plots, SHAP explanations, predictions,
confidence summaries, logs, and JSON reports are written to
`ml/training/reports/`.

The persisted model bundles include the exact selected feature order and the
classification label encoder, making reload and inference reproducible.
