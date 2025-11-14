import asyncio
import uvicorn
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.bot.bot import main as bot_main
from src.core.models import Base
from src.app.main import create_app

async def run_fastapi(app):
    """Запуск FastAPI через uvicorn"""
    config = uvicorn.Config(app)
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    # Создаем папку data если её нет
    os.makedirs('data', exist_ok=True)
    
    # Используем путь в папке data
    db_path = 'data/db.db'
    
    engine = create_async_engine(f'sqlite+aiosqlite:///{db_path}')
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    Session = async_sessionmaker(engine, expire_on_commit=False)
    session = Session()
    
    try:
        app = create_app(session)
        
        if asyncio.iscoroutine(app):
            app = await app
        
        await asyncio.gather(
            run_fastapi(app),
            bot_main(session)
        )
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(main())