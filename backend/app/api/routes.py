from fastapi import APIRouter
from app.api.endpoints import auth, users, dispatches, goods_receipts, items, stl_pedidos, sap_delivery, sap_goods_receipt, telegram_admin
from app.api.v1.endpoints import sync_config

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["authentication"])
router.include_router(users.router, prefix="/users", tags=["users"])
router.include_router(sync_config.router, prefix="/sync-config", tags=["configuration"])
router.include_router(dispatches.router, prefix="/dispatches", tags=["dispatches"])
router.include_router(goods_receipts.router, prefix="/goods-receipts", tags=["goods-receipts"])
router.include_router(items.router, prefix="/items", tags=["items"])
router.include_router(stl_pedidos.router, prefix="/stl/pedidos", tags=["stl-pedidos"])
router.include_router(sap_delivery.router, prefix="/sap/delivery", tags=["sap-delivery"])
router.include_router(sap_goods_receipt.router, prefix="/sap/goods-receipt", tags=["sap-goods-receipt"])
router.include_router(telegram_admin.router, prefix="/telegram-admin", tags=["telegram-admin"])