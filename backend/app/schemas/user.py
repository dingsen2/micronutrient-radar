from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel, UUID4, EmailStr, Field

class UserBase(BaseModel):
    email: EmailStr
    demographics: Dict
    settings: Dict

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserUpdate(UserBase):
    password: Optional[str] = Field(None, min_length=6)

class UserInDBBase(UserBase):
    id: UUID4
    version: int
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    hashed_password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str 