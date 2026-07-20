from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from app.graph.graph_service import GraphService
from app.graph.risk_propagation import propagate_risk
from app.graph.schemas import GraphHealth, GraphResponse
from app.graph.similarity import similar_enterprises

router = APIRouter(prefix="/graph", tags=["economic-graph"])


def _service(request: Request) -> GraphService:
    service = request.app.state.graph_service
    if not service.loaded:
        service.load()
    return service


@router.get("/summary", response_model=GraphResponse)
def summary(request: Request) -> GraphResponse:
    return GraphResponse(result=_service(request).summary())


@router.get("/enterprise/{enterprise_id}", response_model=GraphResponse)
def enterprise(enterprise_id: str, request: Request) -> GraphResponse:
    service = _service(request)
    try:
        from app.graph.query import node_details

        return GraphResponse(
            result=node_details(service.require_graph(), enterprise_id)
        )
    except KeyError as exc:
        raise HTTPException(
            status_code=404, detail=f"Enterprise not found: {enterprise_id}"
        ) from exc


@router.get("/community/{community_id}", response_model=GraphResponse)
def community(community_id: int, request: Request) -> GraphResponse:
    service = _service(request)
    from app.graph.query import community_details

    result = community_details(service.require_graph(), community_id)
    if not result["members"]:
        raise HTTPException(
            status_code=404, detail=f"Community not found: {community_id}"
        )
    return GraphResponse(result=result)


@router.get("/risk-propagation/{enterprise_id}", response_model=GraphResponse)
def risk_propagation(
    enterprise_id: str, request: Request, shock: float = 0.2, max_hops: int = 3
) -> GraphResponse:
    service = _service(request)
    result = propagate_risk(service.require_graph(), enterprise_id, shock, max_hops)
    if (
        not result["affected_nodes"]
        and f"enterprise:{enterprise_id}" not in service.require_graph()
    ):
        raise HTTPException(
            status_code=404, detail=f"Enterprise not found: {enterprise_id}"
        )
    return GraphResponse(result=result)


@router.get("/top-central", response_model=GraphResponse)
def top_central(request: Request, limit: int = 10) -> GraphResponse:
    service = _service(request)
    values = sorted(
        (
            (node, metrics)
            for node, metrics in service.centrality.items()
            if service.require_graph().nodes[node].get("node_type") == "Enterprise"
        ),
        key=lambda item: item[1]["pagerank"],
        reverse=True,
    )[:limit]
    return GraphResponse(
        result={
            "central_enterprises": [
                {"node_id": node, **metrics} for node, metrics in values
            ]
        }
    )


@router.get("/similar/{enterprise_id}", response_model=GraphResponse)
def similar(enterprise_id: str, request: Request, limit: int = 10) -> GraphResponse:
    service = _service(request)
    result = similar_enterprises(service.require_graph(), enterprise_id, limit)
    if not result and f"enterprise:{enterprise_id}" not in service.require_graph():
        raise HTTPException(
            status_code=404, detail=f"Enterprise not found: {enterprise_id}"
        )
    return GraphResponse(
        result={"enterprise_id": enterprise_id, "similar_enterprises": result}
    )


@router.get("/statistics", response_model=GraphResponse)
def statistics(request: Request) -> GraphResponse:
    return GraphResponse(result=_service(request).summary()["statistics"])


@router.get("/health", response_model=GraphHealth)
def health(request: Request) -> GraphHealth:
    service = _service(request)
    graph = service.require_graph()
    return GraphHealth(
        status="ok",
        loaded=service.loaded,
        nodes=graph.number_of_nodes(),
        edges=graph.number_of_edges(),
    )
