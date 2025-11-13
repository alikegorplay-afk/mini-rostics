from typing import TypedDict
from decimal import Decimal

from pydantic import HttpUrl


class ProductMap(TypedDict):
    title: str
    poster: str | HttpUrl
    price: Decimal | int | float
    description: str | None = None
    count: int = 0