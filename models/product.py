# models/product.py

from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, func
from sqlalchemy.orm import relationship
from database.db import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True) 

    name = Column(String, nullable=False)              
    description = Column(String, nullable=True)        

    price = Column(Float, nullable=False)              
    stock = Column(Integer, default=0)                 

    status = Column(String, default="available")      

    farmer_id = Column(Integer, ForeignKey("users.id")) 
    created_at = Column(DateTime, server_default=func.now()) 


    farmer = relationship("User", back_populates="products") 
    order_items = relationship("OrderItem", back_populates="product", cascade="all, delete-orphan") 
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan", order_by="ProductImage.position") 