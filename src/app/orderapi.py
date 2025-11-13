from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database.order import OrderManager
from ..core.models import BaseOrder
from ..core.auth import verify_token

def init_order_api(session: AsyncSession):
    manager = OrderManager(session)
    router = APIRouter(prefix="/api/v1", tags=["orders"])
    
    @router.get("/order/{id}")
    async def get_order(id: int):
        try:
            data = await manager.get_order(id)
            if data:
                return {
                    'ok': True,
                    'data': data.as_dict()
                }
            else:
                raise HTTPException(status_code=404, detail=f"Не найден пользователь по id: {id}")
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    @router.post("/order")
    async def post_order(order: BaseOrder, token: str = Depends(verify_token)):
        try:
            await manager.add_order(order)
            return {
                'ok': True
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    return router