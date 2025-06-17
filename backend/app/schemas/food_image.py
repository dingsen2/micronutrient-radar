from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, Field, UUID4

class FoodItemBase(BaseModel):
    description: str
    quantity: float
    fdc_id: Optional[str] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    is_estimated: bool = False

class FoodItemCreate(FoodItemBase):
    pass

class FoodItemUpdate(FoodItemBase):
    pass

class FoodItemInDBBase(FoodItemBase):
    id: UUID4
    food_image_id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class FoodItem(FoodItemInDBBase):
    pass

class FoodImageBase(BaseModel):
    captured_at: datetime
    image_url: str
    status: str
    recognition_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)

class FoodImageCreate(FoodImageBase):
    food_items: List[FoodItemCreate]

class FoodImageUpdate(FoodImageBase):
    food_items: Optional[List[FoodItemUpdate]] = None

class FoodImageInDBBase(FoodImageBase):
    id: UUID4
    user_id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class FoodImageSchema(FoodImageInDBBase):
    food_items: List[FoodItem]

class FoodImageResponse(FoodImageSchema):
    task_id: Optional[str] = None 