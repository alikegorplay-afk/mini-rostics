from sqlalchemy.ext.asyncio import AsyncSession

from .login import router as login_router
from .start import router as start_router
from .product import init as product_init

def get_router(session: AsyncSession):
    main = [
        login_router,
        start_router
    ]
    
    main.extend(product_init(session))
    
    return main