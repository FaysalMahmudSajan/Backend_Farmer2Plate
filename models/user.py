# models/user.py

from sqlalchemy import Column, Integer, String, Enum, Boolean, DateTime, func, LargeBinary
from sqlalchemy.orm import relationship
from database.db import Base
import enum


class UserRole(str, enum.Enum):
    farmer = "farmer"
    customer = "customer"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    role = Column(Enum(UserRole), default=UserRole.customer)

    is_active = Column(Boolean, default=True) # user active or not
    is_verified = Column(Boolean, default=False) # email verified or not
    otp_code = Column(String, nullable=True) # 5-digit verification code

    # farmer info
    farm_name = Column(String, nullable=True)
    farm_address = Column(String, nullable=True)

    # user location
    address = Column(String, nullable=True)
    latitude = Column(String, nullable=True)      # অক্ষাংশ (ম্যাপের জন্য)
    longitude = Column(String, nullable=True)     # দ্রাঘিমাংশ (ম্যাপের জন্য)

    # প্রোফাইল পিকচার — binary data সরাসরি DB তে (product image এর মতো)
    profile_picture_data = Column(LargeBinary, nullable=True)
    profile_picture_type = Column(String, nullable=True)  # MIME type, যেমন image/webp

    # অ্যাকাউন্ট তৈরির সময় সংরক্ষণ করা হবে (অটো-জেনারেটেড)
    created_at = Column(DateTime, server_default=func.now())

    # রিলেশনশিপ (এক ইউজারের একাধিক প্রোডাক্ট ও অর্ডার থাকতে পারে, ইউজার ডিলিট হলে এগুলোও ডিলিট হবে)
    products = relationship("Product", back_populates="farmer", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="customer", cascade="all, delete-orphan")

class OTPRecord(Base):
    __tablename__ = "otp_records"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    otp_code = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())