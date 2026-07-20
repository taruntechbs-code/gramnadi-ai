from app.models.loan import Loan
from app.schemas.loan import LoanCreate, LoanUpdate
from app.services.base import CRUDService


class LoanService(CRUDService[Loan, LoanCreate, LoanUpdate]):
    model = Loan
    resource_name = "loan"
