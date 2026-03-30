# schemas/customer.py

from pydantic import BaseModel
from typing import Optional

class RequestOTP(BaseModel):
    email: str

# নতুন কাস্টমার অ্যাকাউন্ট খোলার সময় যে ডাটাগুলো রিসিভ করা হবে
class CustomerRegister(BaseModel):
    name: str # কাস্টমারের নাম
    phone: str # মোবাইল নম্বর
    email: str # ইমেইল
    password: str # পাসওয়ার্ড
    otp: str # OTP কোড
    address: Optional[str] = None # ঠিকানা (ঐচ্ছিক)
    latitude: Optional[str] = None # অক্ষাংশ (ম্যাপের জন্য)
    longitude: Optional[str] = None # দ্রাঘিমাংশ (ম্যাপের জন্য)

# কাস্টমার লগইন এর সময় যেসব ডাটা লাগবে
class CustomerLogin(BaseModel):
    email: str
    password: str

# ফ্রন্টএন্ডে কাস্টমারের তথ্য দেখানোর জন্য রেসপন্স স্কিমা
class CustomerResponse(BaseModel):
    id: int
    name: str
    phone: str
    email: str
    address: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None

    class Config:
        from_attributes = True

# কাস্টমারের প্রোফাইলের ডাটা আপডেট করার স্কিমা
class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None