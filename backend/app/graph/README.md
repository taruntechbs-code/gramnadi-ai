# Village Economic Knowledge Graph

Phase 5 builds a cached, weighted NetworkX property graph from the existing
Phase 2 rural enterprise panel and its Phase 3 metadata. It models enterprises,
villages, commodities, weather regions, loan clusters, and risk clusters with
explainable relationship attributes. Community detection, centrality,
similarity, neighborhood queries, analytics, and deterministic risk
propagation are available through the graph API.

The graph is built once during FastAPI startup and reused for requests. Reports
are written to `backend/app/graph/reports/`. No graph neural networks,
retraining, dataset regeneration, counterfactual simulation, or Phase 6 work
is included.
