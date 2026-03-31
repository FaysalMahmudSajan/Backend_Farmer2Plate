# models/order.py

from sqlalchemy import Column, Integer, ForeignKey, Float, String, DateTime
from sqlalchemy.orm import relationship
from database.db import Base
from datetime import datetime, timezone

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True) 

    customer_id = Column(Integer, ForeignKey("users.id")) 

    total_price = Column(Float, nullable=False) 

    status = Column(String, default="pending")  

    delivery_address = Column(String, nullable=True) 

    payment_method = Column(String, default="cod", nullable=True)  

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc)) 

    customer = relationship("User", back_populates="orders") 
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan") 