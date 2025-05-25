from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, UUID4

class FoodItemBase(BaseModel):
    description: str
    quantity: float
    fdc_id: Optional[str] = None
    confidence: Optional[float] = None
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
    recognition_confidence: Optional[float] = None

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

class FoodImage(FoodImageInDBBase):
    food_items: List[FoodItem]

class NutrientLedgerBase(BaseModel):
    week_start: datetime
    nutrient: Dict
    percent_rda: Dict
    data_source: str

class NutrientLedgerCreate(NutrientLedgerBase):
    pass

class NutrientLedgerUpdate(NutrientLedgerBase):
    pass

class NutrientLedgerInDBBase(NutrientLedgerBase):
    id: UUID4
    user_id: UUID4
    last_updated: datetime

    class Config:
        from_attributes = True

class NutrientLedger(NutrientLedgerInDBBase):
    pass 