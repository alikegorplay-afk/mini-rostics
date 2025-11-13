__all__ = [
    "OrderManager"
]

from sqlalchemy.engine.result import ScalarResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from loguru import logger

from ..models import Order, BaseOrder, OrderItem

class OrderManager:
    def __init__(self, session: AsyncSession):
        if not isinstance(session, AsyncSession):
            raise TypeError("Переданный тип не является асинхронной сессией")
        self.session = session
        
    async def add_order(self, order: Order):
        logger.info("Попытка добавить заказ в базу данных")
        if not isinstance(order, (Order, BaseOrder)):
            logger.error("Переданный тип данных не является классом Order")
            raise TypeError("Переданный тип данных не является классом Order")
            
        elif not order.order_items:
            logger.error("Заказ должен иметь хотя-бы 1 атрибут OrderItem")
            raise ValueError("Заказ должен иметь хотя-бы 1 атрибут OrderItem")
        
        if isinstance(order, BaseOrder):
            try:
                new_order = Order()
                for item in order.order_items:
                    new_order.append(OrderItem(**item.as_dict()))
                order = new_order
            except Exception as e:
                logger.error(e)
            
        self.session.add(order)
        try:
            await self.session.commit()
            await self.session.refresh(order, ['id'])
            logger.success(f"Заказ создан, номер заказа: {order.id}")
        except Exception as e:
            logger.error(f"Не удалось добавить заказ причина: '{e}'")
            raise e
        
    async def get_order(self, id: int):
        logger.info(f"Попытка получить заказ под номером: {id}")
        try:
            stmt = select(Order).where(Order.id == id).options(
                selectinload(Order.order_items)
            )
            result = await self.session.scalar(stmt)
            if result:
                logger.success(f"Был найден заказ под id {id}")
            else:
                logger.warning(f"Не найден заказ под id {id}")
            return result
        except Exception as e:
            logger.error(f"Не удалось достать заказ, по причине: {e}")
            raise e
                
    async def orders(self) -> ScalarResult[Order]:
        mrt = select(Order)
        return await self.session.scalars(mrt)