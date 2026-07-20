class ServiceError(Exception):
    """Base exception for application service failures."""


class ResourceNotFoundError(ServiceError):
    def __init__(self, resource: str, resource_id: object) -> None:
        super().__init__(f"{resource} '{resource_id}' was not found")


class ConflictError(ServiceError):
    """Raised when persistence violates a uniqueness or relationship constraint."""


class DomainValidationError(ServiceError):
    """Raised when a cross-field domain invariant is invalid."""
