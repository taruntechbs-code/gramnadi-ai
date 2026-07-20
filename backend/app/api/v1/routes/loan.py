from app.api.v1.routes.crud import build_crud_router
from app.schemas.loan import LoanCreate, LoanResponse, LoanUpdate
from app.services.loan import LoanService

router = build_crud_router(
    resource_path="loans",
    resource_name="loan",
    tag="Loans",
    create_schema=LoanCreate,
    update_schema=LoanUpdate,
    response_schema=LoanResponse,
    service_factory=LoanService,
)
