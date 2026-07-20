from app.models.commodity_price import CommodityPrice
from app.schemas.commodity_price import CommodityPriceCreate, CommodityPriceUpdate
from app.services.base import CRUDService


class CommodityPriceService(
    CRUDService[CommodityPrice, CommodityPriceCreate, CommodityPriceUpdate]
):
    model = CommodityPrice
    resource_name = "commodity price"
