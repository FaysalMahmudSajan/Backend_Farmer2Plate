# schemas/farmer.py

from pydantic import BaseModel
from typing import Optional

class RequestOTP(BaseModel):
    email: str

class FarmerRegister(BaseModel):
    name: str
    phone: str
    email: str
    password: str
    otp: str
    farm_name: str
    farm_address: str
    latitude: Optional[str] = None
    longitude: Optional[str] = None


class FarmerLogin(BaseModel):
    email: str
    password: str


class FarmerResponse(BaseModel):
    id: int
    name: str
    phone: str
    email: str
    farm_name: Optional[str] = None
    farm_address: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None

    class Config:
        from_attributes = True


class FarmerUpdate(BaseModel):
    name: Optional[str] = None
    farm_name: Optional[str] = None
    farm_address: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None