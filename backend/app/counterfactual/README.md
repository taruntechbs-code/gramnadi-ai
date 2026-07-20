# Phase 6 Counterfactual Recommendation Engine

This package performs bounded, algorithmic counterfactual search using the
existing Phase 4 predictor and Phase 5 graph. It does not retrain models or
use an LLM. Candidate changes are constrained for non-negative finances,
physical weather ranges, loan consistency, limited growth, and simple
implementation. Candidates are simulated through the existing ML inference
path, scored by projected cash-flow improvement, risk reduction, cost, and
complexity, and reduced to the top five.

Endpoints:

- `POST /api/v1/recommend`
- `POST /api/v1/recommend/batch`
- `GET /api/v1/recommend/history/{enterprise_id}`
- `GET /api/v1/recommend/health`

The request uses the same 264-feature model-ready payload accepted by the ML
API. Results and simulation reports are written under
`backend/app/counterfactual/reports/`.
