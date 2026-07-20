from app.models.financial_record import FinancialRecord
from app.schemas.financial_record import (
    FinancialRecordCreate,
    FinancialRecordUpdate,
    validate_financial_period,
)
from app.services.base import CRUDService
from app.services.exceptions import DomainValidationError


class FinancialRecordService(
    CRUDService[FinancialRecord, FinancialRecordCreate, FinancialRecordUpdate]
):
    model = FinancialRecord
    resource_name = "financial record"

    def create(self, payload: FinancialRecordCreate) -> FinancialRecord:
        self._validate_period(payload.month, payload.year)
        return super().create(payload)

    def update(self, resource_id, payload: FinancialRecordUpdate) -> FinancialRecord:
        resource = self.get(resource_id)
        values = payload.model_dump(exclude_unset=True)
        month = values.get("month", resource.month)
        year = values.get("year", resource.year)
        self._validate_period(month, year)
        return super().update(resource_id, payload)

    @staticmethod
    def _validate_period(month: int, year: int) -> None:
        try:
            validate_financial_period(month, year)
        except ValueError as exc:
            raise DomainValidationError(str(exc)) from exc
