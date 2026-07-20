# Phase 4 ML inference

The inference service loads the immutable Phase 3B model bundles once during
FastAPI startup. It also loads `ml/processed/pipeline_artifact.joblib`, which
contains the Phase 3A encoder, scaler, and feature ordering. Requests can use
the exported model-ready 264-feature vector or a raw Phase 2-style payload;
raw payloads are passed through the existing Phase 3A `FeatureBuilder` and
persisted encoder/scaler.

Endpoints:

- `POST /api/v1/ml/predict`
- `POST /api/v1/ml/batch-predict`
- `GET /api/v1/ml/model-info`
- `GET /api/v1/ml/health`

Example request:

```json
{
  "enterprise_id": "enterprise-001",
  "features": {"employees": 4, "annual_turnover": 120000}
}
```

In production, `features` must contain all 264 Phase 3A model-ready features,
or all fields required by the raw Phase 2 schema. Configure artifact paths
with `GRAMNADI_MODEL_DIR` and `GRAMNADI_PROCESSED_DIR`; confidence thresholds,
batch limits, and SHAP can also be configured with the `ML_*` environment
variables.
