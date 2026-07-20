from fastapi import APIRouter

from app.api.v1.routes import (
    commodity_price,
    counterfactual_simulation,
    enterprise,
    financial_record,
    health,
    intervention,
    loan,
    prediction,
    prediction_explanation,
    village_graph_edge,
    village_graph_node,
    weather_snapshot,
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["platform"])
api_router.include_router(enterprise.router)
api_router.include_router(financial_record.router)
api_router.include_router(loan.router)
api_router.include_router(commodity_price.router)
api_router.include_router(weather_snapshot.router)
api_router.include_router(prediction.router)
api_router.include_router(prediction_explanation.router)
api_router.include_router(intervention.router)
api_router.include_router(counterfactual_simulation.router)
api_router.include_router(village_graph_node.router)
api_router.include_router(village_graph_edge.router)
