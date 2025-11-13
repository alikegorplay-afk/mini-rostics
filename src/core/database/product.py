__all__ = [
    "ProductManager"
]

from typing import Unpack, Any, List
from pydantic import ValidationError

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

from ...errors import ProductNotFindError
from ...types._types import ProductMap
from ..models import BaseProduct, Product

class ProductManager:
    def __init__(self, session: AsyncSession):
        if not isinstance(session, AsyncSession):
            raise TypeError("Переданный тип не является асинхронной сессией")
        self.session = session
    
    async def get_product(self, id: int) -> Product | None:
        logger.info(f"Попытка получить продукт под номером: {id}")
        try:
            result = await self.session.get(Product, id)
            if result:
                logger.success(f"Был найден продукт под id {id} ({repr(result)})")
            else:
                logger.warning(f"Не найден продукт под id {id}")
            return result
        except Exception as e:
            logger.error(f"Не удалось достать продукт, по причине: {e}")
            raise e
    
    async def get_all_product(self) -> List[Product]:
        logger.info("Попытка получить все продукты")
        mrt = select(Product)
        result = list(await self.session.scalars(mrt))
        logger.info(f"Было получено {len(result)} товаров")
        return result
        
    async def create_product(self, **kw: Unpack[ProductMap]):
        logger.info(f"Попытка добавить продукт '{kw.get("title", "unknown")}'")
        try:
            base_product = BaseProduct(**kw)
            product = Product(**base_product.to_dict())
            self.session.add(product)
            await self.session.commit()
            await self.session.refresh(product)
            logger.success(f"Продукт {product.id} был добавлен")
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Неизвестаня ошибка: {e}")
            raise e
        
    async def delete_product(self, id: int):
        logger.info(f"Попытка удалить продукт {id}")
        item = await self.session.get(Product, id)
        if not item:
            logger.warning(f"Продукт под id {id} не обнаружен")
            raise ProductNotFindError(f"Продукт под id {id} не обнаружен")
        try:
            await self.session.delete(item)
            await self.session.commit()
            logger.success(f"Продукт {id} был удалён")
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Неизвестаня ошибка: {e}")
            raise e
        
    async def custom_product(self, id: int, key: str, value: Any):
        if not hasattr(Product, key):
            raise AttributeError(f"Класс продукт не имеет атрибут: {key}")
        
        item = await self.session.get(Product, id)
        if not item:
            logger.warning(f"Продукт под id {id} не обнаружен")
            raise ProductNotFindError(f"Продукт под id {id} не обнаружен")
        
        current_data = item.as_dict()
        
        try:
            updated_data = current_data.copy()
            updated_data[key] = value
            
            validated_data = BaseProduct(**updated_data).to_dict()

            setattr(item, key, validated_data[key])
            await self.session.commit()
            
            logger.info(f"Продукт {id} успешно обновлен: {key} = {value}")
            return item
            
        except ValidationError as e:
            await self.session.rollback()
            logger.error(f"Ошибка валидации для продукта {id}: {e}")
            raise e
        
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Неизвестная ошибка: {e}")
            raise e
            