
from pydantic import BaseModel
from typing import Optional

class RequestOTP(BaseModel):
    email: str

class CustomerRegister(BaseModel):
    name: str 
    phone: str 
    email: str 
    password: str 
    otp: str 
    address: Optional[str] = None 
    latitude: Optional[str] = None 
    longitude: Optional[str] = None 


class CustomerLogin(BaseModel):
    email: str
    password: str

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

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None