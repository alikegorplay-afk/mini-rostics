from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager

from .productapi import init_api
from .orderapi import init_order_api

async def create_app(session: AsyncSession):
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.include_router(init_api(session))
        app.include_router(init_order_api(session))
        yield

    app = FastAPI(lifespan=lifespan)
    return app