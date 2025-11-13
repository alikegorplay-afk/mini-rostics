from dataclasses import dataclass
from typing import Iterable, Dict, Any, Hashable

from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text, Float, ForeignKey, Integer
from sqlalchemy.ext.asyncio import AsyncAttrs

class Base(AsyncAttrs, DeclarativeBase): ...


@dataclass
class Product(Base):
    __tablename__ = "product"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    poster: Mapped[str] = mapped_column(String(1024))
    price: Mapped[float] = mapped_column(Float())
    description: Mapped[str] = mapped_column(Text(), nullable=True)
    count: Mapped[int] = mapped_column(Integer())
    
    def as_dict(self) -> Dict[Hashable, Any]:
        return {
            'id': self.id,
            'title': self.title,
            'poster': self.poster,
            'price': self.price,
            'description': self.description,
            'count': self.count
        }


@dataclass(repr=False)
class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)

    order_items: Mapped[list["OrderItem"]] = relationship("OrderItem", back_populates="order")
    
    def append(self, value: "OrderItem"):
        if not isinstance(value, OrderItem):
            raise TypeError("Переданный элемент не является OrderItem")
        
        self.order_items.append(value)
    
    def extend(self, values: Iterable["OrderItem"]):
        for value in values:
            self.append(value)
    
    def __repr__(self):
        return (f"Order(id={self.id}, order_items={len(self.order_items)})")
    
    def __len__(self):
        return len(self.order_items)
        
    def as_dict(self):
        return {
            'id': self.id,
            'order_items': [x.as_dict() for x in self.order_items]
        }


@dataclass(repr=False)
class OrderItem(Base):
    __tablename__ = "order_item"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"))
    count: Mapped[int] = mapped_column(Integer()) 
    
    order: Mapped["Order"] = relationship("Order", back_populates="order_items")
    product: Mapped["Product"] = relationship("Product")
    
    def __repr__(self):
        return (
            "OrderItem"
            f"(id={self.id}, order_id={self.order_id}, product_id={self.product_id}, count={self.count})"
        )
        
    def as_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'count': self.count
        }