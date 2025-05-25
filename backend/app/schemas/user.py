from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from uuid import UUID

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    demographics: Dict[str, Any]
    settings: Dict[str, Any]

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    demographics: Dict[str, Any]
    settings: Dict[str, Any]

    class Config:
        from_attributes = True 