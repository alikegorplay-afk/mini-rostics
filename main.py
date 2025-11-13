import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.bot.bot import main as bot_main
from src.core.models import Base

async def main():
    engine = create_async_engine('sqlite+aiosqlite:///db.db')
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    Session = async_sessionmaker(engine)
    
    async with Session() as session:
        await bot_main(session)


if __name__ == "__main__":
    asyncio.run(main())