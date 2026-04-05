# schemas/customer.py

from pydantic import BaseModel, model_validator
from typing import Optional, Any

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
    has_profile_picture: bool = False 

    class Config:
        from_attributes = True

    @model_validator(mode='before')
    @classmethod
    def set_has_profile_picture(cls, data: Any):
        if hasattr(data, 'profile_picture_data'):
            object.__setattr__(data, '_has_pic', bool(data.profile_picture_data))
        return data

    @model_validator(mode='after')
    def fill_has_profile_picture(self):
        return self
    
class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None