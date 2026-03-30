# schemas/order.py

from pydantic import BaseModel
from typing import Optional
from schemas.order_item import OrderItemCreate, OrderItemResponse

# নতুন অর্ডার করার সময় যে ডাটাগুলো রিসিভ করা হবে
class OrderCreate(BaseModel):
    items: list["OrderItemCreate"] # কী কী আইটেম অর্ডার করা হলো তার লিস্ট
    delivery_address: str # ডেলিভারি ঠিকানা
    payment_method: Optional[str] = "cod" # পেমেন্ট পদ্ধতি (ডিফল্ট: ক্যাশ অন ডেলিভারি)

# ফ্রন্টএন্ডে অর্ডারের ডিটেইলস দেখানোর স্কিমা
class OrderResponse(BaseModel):
    id: int
    customer_id: int # কে অর্ডার করেছে
    total_price: float # মোট দাম কত
    status: str # অর্ডারের বর্তমান অবস্থা (যেমন: পেন্ডিং, শিফট ইত্যাদি)
    delivery_address: Optional[str] = None
    payment_method: Optional[str] = "cod" # পেমেন্ট পদ্ধতি
    created_at: Optional[str] = None # অর্ডারের তারিখ
    items: list["OrderItemResponse"] # অর্ডারের ভেতরে থাকা আইটেমগুলোর লিস্ট

    class Config:
        from_attributes = True
