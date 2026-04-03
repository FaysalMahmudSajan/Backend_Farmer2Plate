# schemas/customer.py

from pydantic import BaseModel, model_validator
from typing import Optional, Any

class RequestOTP(BaseModel):
    email: str

# নতুন কাস্টমার অ্যাকাউন্ট খোলার সময় যে ডাটাগুলো রিসিভ করা হবে
class CustomerRegister(BaseModel):
    name: str # কাস্টমারের নাম
    phone: str # মোবাইল নম্বর
    email: str # ইমেইল
    password: str # পাসওয়ার্ড
    otp: str # OTP কোড
    address: Optional[str] = None # ঠিকানা (ঐচ্ছিক)
    latitude: Optional[str] = None # অক্ষাংশ (ম্যাপের জন্য)
    longitude: Optional[str] = None # দ্রাঘিমাংশ (ম্যাপের জন্য)

# কাস্টমার লগইন এর সময় যেসব ডাটা লাগবে
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
    has_profile_picture: bool = False  # binary data আছে কিনা (frontend জানাবে)

    class Config:
        from_attributes = True

    @model_validator(mode='before')
    @classmethod
    def set_has_profile_picture(cls, data: Any):
        if hasattr(data, 'profile_picture_data'):
            # SQLAlchemy model object
            object.__setattr__(data, '_has_pic', bool(data.profile_picture_data))
        return data

    @model_validator(mode='after')
    def fill_has_profile_picture(self):
        # ORM object থেকে set করা হয়েছিল কিনা
        return self

# কাস্টমারের প্রোফাইলের ডাটা আপডেট করার স্কিমা
class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None