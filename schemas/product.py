# schemas/product.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# নতুন প্রোডাক্ট তৈরি করার সময় API তে যে রিকোয়েস্ট বডি আসবে
class ProductCreate(BaseModel):
    name: str # প্রোডাক্টের নাম
    description: Optional[str] = None # প্রোডাক্টের বিবরণ (ঐচ্ছিক)
    price: float # প্রোডাক্টের দাম
    stock: int # স্টকে পরিমাণ

# প্রোডাক্ট আপডেট করার সময় API তে যে ডাটা আসতে পারে
class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    status: Optional[str] = None # প্রোডাক্টের স্ট্যাটাস (available / out_of_stock)

# প্রোডাক্টের ছবি ফ্রন্টএন্ডে পাঠানোর জন্য স্কিমা
class ProductImageResponse(BaseModel):
    id: int
    position: int # ছবির সিরিয়াল
    content_type: str # ছবির টাইপ (যেমন: image/webp)

    class Config:
        from_attributes = True # SQLAlchemy মডেল থেকে Pydantic মডেল এ কনভার্ট করার জন্য

# ফ্রন্টএন্ডে প্রোডাক্টের ডিটেইলস দেখানোর রেসপন্স স্কিমা
class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    status: str
    farmer_id: int
    created_at: Optional[datetime] = None # প্রোডাক্ট তৈরির তারিখ
    images: list[ProductImageResponse] = [] # প্রোডাক্টের সাথে যুক্ত সব ছবি

    class Config:
        from_attributes = True