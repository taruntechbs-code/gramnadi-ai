from app.api.v1.routes.crud import build_crud_router
from app.schemas.commodity_price import (
    CommodityPriceCreate,
    CommodityPriceResponse,
    CommodityPriceUpdate,
)
from app.services.commodity_price import CommodityPriceService

router = build_crud_router(
    resource_path="commodity-prices",
    resource_name="commodity price",
    tag="Commodity Prices",
    create_schema=CommodityPriceCreate,
    update_schema=CommodityPriceUpdate,
    response_schema=CommodityPriceResponse,
    service_factory=CommodityPriceService,
)
