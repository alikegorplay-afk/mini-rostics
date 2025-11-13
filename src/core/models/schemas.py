from decimal import Decimal
from typing import Any, List

from pydantic import BaseModel, HttpUrl, field_validator


class Product(BaseModel):
    title: str
    poster: HttpUrl | str
    price: Decimal | float
    description: str | None = None
    count: int = 0
    
    @field_validator('price')
    def price_validator(cls, value: Any):
        if value < 0:
            raise ValueError("Стоимость продукта не может быть отрицательной")
        return value
    
    @field_validator('count')
    def count_validator(cls, value: Any):
        if value < 0:
            raise ValueError("Количество продукта не может быть отрицательной")
        return value
    
    def to_dict(self):
        return {
            'title': self.title,
            'poster': str(self.poster),
            'price': self.price,
            'description': self.description,
            'count': self.count
        }
        
class OrderItem(BaseModel):
    product_id: int
    count: int
    
    def as_dict(self):
        return {
            'product_id': self.product_id,
            'count': self.count
        }

class Order(BaseModel):
    order_items: List[OrderItem]
    
    def as_dict(self):
        return {
            'order_items': [x.to_dict() for x in self.order_items]
        }