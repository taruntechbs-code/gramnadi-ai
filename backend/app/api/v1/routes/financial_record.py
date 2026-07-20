from app.api.v1.routes.crud import build_crud_router
from app.schemas.financial_record import (
    FinancialRecordCreate,
    FinancialRecordResponse,
    FinancialRecordUpdate,
)
from app.services.financial_record import FinancialRecordService

router = build_crud_router(
    resource_path="financial-records",
    resource_name="financial record",
    tag="Financial Records",
    create_schema=FinancialRecordCreate,
    update_schema=FinancialRecordUpdate,
    response_schema=FinancialRecordResponse,
    service_factory=FinancialRecordService,
)
