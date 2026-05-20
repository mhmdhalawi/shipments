from routes.shipments import router as shipments_router
from routes.ai import router as ai_router
from routes.sellers import router as seller_router
from routes.delivery_partners import router as delivery_partner_router


__all__ = ["shipments_router", "ai_router", "seller_router", "delivery_partner_router"]
