# schemas/product.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProductCreate(BaseModel):
    name: str 
    description: Optional[str] = None 
    price: float 
    stock: int 

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    status: Optional[str] = None 

class ProductImageResponse(BaseModel):
    id: int
    position: int 
    content_type: str 

    class Config:
        from_attributes = True 

class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    status: str
    farmer_id: int
    created_at: Optional[datetime] = None 
    images: list[ProductImageResponse] = [] 

    class Config:
        from_attributes = True