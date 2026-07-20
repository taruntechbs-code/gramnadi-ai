from app.models.enterprise import Enterprise
from app.schemas.enterprise import EnterpriseCreate, EnterpriseUpdate
from app.services.base import CRUDService


class EnterpriseService(CRUDService[Enterprise, EnterpriseCreate, EnterpriseUpdate]):
    model = Enterprise
    resource_name = "enterprise"
