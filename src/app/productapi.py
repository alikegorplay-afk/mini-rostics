from typing import Any
from pydantic import ValidationError
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database.product import ProductManager
from ..core.models import BaseProduct
from ..errors import ProductNotFindError
from ..core.auth import verify_token

def init_api(session: AsyncSession):
    manager = ProductManager(session)
    router = APIRouter(prefix="/api/v1", tags=["products"])
    
    @router.get("/getMe")
    async def get_me():
        return {'ok': True}

    @router.get("/allProduct")
    async def all_product(token: str = Depends(verify_token)):
        try:
            products = await manager.get_all_product()
            return {
                'ok': True,
                'data': [x.as_dict() for x in products]
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/product/{id}")
    async def get_product(id: int):
        try:
            product = await manager.get_product(id)
            return {
                'ok': True,
                'data': product
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/product")
    async def add_product(data: BaseProduct, token: str = Depends(verify_token)):
        try:
            await manager.create_product(**data.model_dump())  
            return {'ok': True}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.delete("/product/{id}")
    async def delete_product(id: int, token: str = Depends(verify_token)):
        try:
            await manager.delete_product(id)
            return {'ok': True}
        except ProductNotFindError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            
    @router.patch("/product/{id}")
    async def custom_product(id: int, key: str, value: Any, token: str = Depends(verify_token)):
        try:
            await manager.custom_product(id, key, value)
            return {'ok': True}
        except ValidationError as e:
            raise HTTPException(status_code=422, detail=str(e))
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    return router