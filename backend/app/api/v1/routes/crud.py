from collections.abc import Callable
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.base import CRUDService


def build_crud_router(
    *,
    resource_path: str,
    resource_name: str,
    tag: str,
    create_schema: type[BaseModel],
    update_schema: type[BaseModel],
    response_schema: type[BaseModel],
    service_factory: Callable[[Session], CRUDService[Any, Any, Any]],
) -> APIRouter:
    router = APIRouter(prefix=f"/{resource_path}", tags=[tag])

    def list_resources(
        skip: int = Query(0, ge=0, description="Number of records to skip."),
        limit: int = Query(
            100, ge=1, le=1000, description="Maximum number of records to return."
        ),
        db: Session = Depends(get_db),
    ) -> list[Any]:
        return list(service_factory(db).list(skip=skip, limit=limit))

    def get_resource(resource_id: UUID, db: Session = Depends(get_db)) -> Any:
        return service_factory(db).get(resource_id)

    def create_resource(payload: create_schema, db: Session = Depends(get_db)) -> Any:
        return service_factory(db).create(payload)

    def update_resource(
        resource_id: UUID,
        payload: update_schema,
        db: Session = Depends(get_db),
    ) -> Any:
        return service_factory(db).update(resource_id, payload)

    def delete_resource(resource_id: UUID, db: Session = Depends(get_db)) -> Response:
        service_factory(db).soft_delete(resource_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    route_responses = {
        404: {"description": f"The {resource_name} was not found."},
        409: {"description": f"The {resource_name} conflicts with existing data."},
    }
    router.add_api_route(
        "",
        list_resources,
        methods=["GET"],
        response_model=list[response_schema],
        summary=f"List {resource_name}s",
        description=f"Return active {resource_name} records with offset pagination.",
        operation_id=f"list_{resource_path}",
    )
    router.add_api_route(
        "/{resource_id}",
        get_resource,
        methods=["GET"],
        response_model=response_schema,
        summary=f"Get a {resource_name}",
        description=f"Return one active {resource_name} by UUID.",
        operation_id=f"get_{resource_path[:-1]}",
        responses=route_responses,
    )
    router.add_api_route(
        "",
        create_resource,
        methods=["POST"],
        response_model=response_schema,
        status_code=status.HTTP_201_CREATED,
        summary=f"Create a {resource_name}",
        description=(
            f"Persist a new {resource_name} after schema and database validation."
        ),
        operation_id=f"create_{resource_path}",
        responses=route_responses,
    )
    router.add_api_route(
        "/{resource_id}",
        update_resource,
        methods=["PUT"],
        response_model=response_schema,
        summary=f"Update a {resource_name}",
        description=f"Update supplied fields on an active {resource_name}.",
        operation_id=f"update_{resource_path}",
        responses=route_responses,
    )
    router.add_api_route(
        "/{resource_id}",
        delete_resource,
        methods=["DELETE"],
        status_code=status.HTTP_204_NO_CONTENT,
        summary=f"Delete a {resource_name}",
        description=(
            f"Soft-delete an active {resource_name}; the row remains recoverable "
            "at the database layer."
        ),
        operation_id=f"delete_{resource_path}",
        responses={404: route_responses[404]},
    )
    return router
