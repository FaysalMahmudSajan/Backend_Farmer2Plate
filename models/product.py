# models/product.py

from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, func
from sqlalchemy.orm import relationship
from database.db import Base

# প্রোডাক্ট বা পণ্যের মডেল (products টেবিল তৈরি করবে)
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True) # প্রোডাক্টের ইউনিক আইডি

    name = Column(String, nullable=False)              # প্রোডাক্টের নাম
    description = Column(String, nullable=True)        # প্রোডাক্টের বর্ণনা (ঐচ্ছিক)

    price = Column(Float, nullable=False)              # প্রোডাক্টের দাম
    stock = Column(Integer, default=0)                 # স্টকে কতগুলো আছে তার পরিমাণ

    status = Column(String, default="available")       # অবস্থা: available (আছে) / out_of_stock (নাই)

    farmer_id = Column(Integer, ForeignKey("users.id")) # কোন কৃষক প্রোডাক্টটি যোগ করেছেন তার আইডি
    created_at = Column(DateTime, server_default=func.now()) # প্রোডাক্ট কবে তৈরি বা যোগ করা হয়েছে

    # ডাটাবেস টেবিলগুলোর মধ্যে রিলেশনশিপ
    farmer = relationship("User", back_populates="products") # কৃষকের সাথে প্রোডাক্টের সম্পর্ক
    order_items = relationship("OrderItem", back_populates="product", cascade="all, delete-orphan") # অর্ডার করা প্রোডাক্ট
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan", order_by="ProductImage.position") # প্রোডাক্টের ছবিগুলো (সিরিয়াল অনুযায়ী)