# models/order.py

from sqlalchemy import Column, Integer, ForeignKey, Float, String, DateTime
from sqlalchemy.orm import relationship
from database.db import Base
from datetime import datetime, timezone

# অর্ডারের মডেল (orders টেবিল তৈরি করবে)
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True) # অর্ডারের ইউনিক আইডি

    customer_id = Column(Integer, ForeignKey("users.id")) # কোন কাস্টমার অর্ডার করেছেন তার আইডি

    total_price = Column(Float, nullable=False) # অর্ডারের মোট দাম

    status = Column(String, default="pending")  
    # অর্ডারের অবস্থা: pending (অপেক্ষমান) / accepted (গৃহীত) / shipped (পাঠানো হয়েছে) / delivered (পৌঁছেছে)

    delivery_address = Column(String, nullable=True) # ডেলিভারি বা পৌঁছানোর ঠিকানা

    payment_method = Column(String, default="cod", nullable=True)  # পেমেন্ট পদ্ধতি: cod (ক্যাশ অন ডেলিভারি) / card

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc)) # অর্ডার কবে করা হয়েছে

    # ডাটাবেস রিলেশনশিপ
    customer = relationship("User", back_populates="orders") # কাস্টমারের সাথে অর্ডারের সম্পর্ক
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan") # এই অর্ডারে কী কী আইটেম আছে তার সম্পর্ক