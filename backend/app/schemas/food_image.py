from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from uuid import UUID

class FoodItemBase(BaseModel):
    description: str
    quantity: float
    confidence: float = Field(ge=0.0, le=1.0)
    is_estimated: bool = True

class FoodItemCreate(FoodItemBase):
    pass

class FoodItem(FoodItemBase):
    id: UUID
    food_image_id: UUID
    created_at: datetime
    updated_at: datetime
    

    class Config:
        from_attributes = True

class FoodImageBase(BaseModel):
    captured_at: datetime
    image_url: str
    status: str
    recognition_confidence: float

class FoodImageCreate(FoodImageBase):
    pass

class FoodImageResponse(FoodImageBase):
    id: UUID
    user_id: UUID
    task_id: Optional[str] = None
    food_items: List[FoodItem] = []

    class Config:
        from_attributes = True 