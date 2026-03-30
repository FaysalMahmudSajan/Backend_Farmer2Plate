# models/order_item.py

from sqlalchemy import Column, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship
from database.db import Base

# অর্ডারের মধ্যে থাকা প্রতিটি প্রোডাক্টের রেকর্ড বা আইটেমের মডেল (order_items টেবিল)
class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True) # আইটেমের ইউনিক আইডি

    order_id = Column(Integer, ForeignKey("orders.id")) # কোন অর্ডারের অংশ এটি
    product_id = Column(Integer, ForeignKey("products.id")) # কোন প্রোডাক্টটি অর্ডার করা হয়েছে

    quantity = Column(Integer, nullable=False) # কতগুলো প্রোডাক্ট বা পরিমাণ অর্ডার করা হয়েছে
    price = Column(Float, nullable=False)      # কেনার সময় ওই প্রোডাক্টের দাম কত ছিল

    # রিলেশনশিপ
    order = relationship("Order", back_populates="items") # মূল অর্ডারের সাথে সম্পর্ক
    product = relationship("Product", back_populates="order_items") # আসল প্রোডাক্টের সাথে সম্পর্ক