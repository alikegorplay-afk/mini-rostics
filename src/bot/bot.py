from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from ..core.config import config
from .handlers import get_router

async def main(session: AsyncSession):
    bot = Bot(token=config.BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    routers = get_router(session)
    
    dp.include_routers(*routers)
    
    await dp.start_polling(bot)