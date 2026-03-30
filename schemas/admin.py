# schemas/admin.py

from pydantic import BaseModel
from typing import Optional

class AdminLogin(BaseModel):
    email: str
    password: str


class AdminLoginResponse(BaseModel):
    access_token: str
    token_type: str


class AdminResponse(BaseModel):
    id: int
    name: str
    phone: str
    email: str
    role: Optional[str] = None

    class Config:
        from_attributes = True