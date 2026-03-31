
from pydantic import BaseModel
from typing import Optional
from schemas.order_item import OrderItemCreate, OrderItemResponse

class OrderCreate(BaseModel):
    items: list["OrderItemCreate"]
    delivery_address: str 
    payment_method: Optional[str] = "cod" 


class OrderResponse(BaseModel):
    id: int
    customer_id: int 
    total_price: float 
    status: str 
    delivery_address: Optional[str] = None
    payment_method: Optional[str] = "cod" 
    created_at: Optional[str] = None 
    items: list["OrderItemResponse"] 

    class Config:
        from_attributes = True
