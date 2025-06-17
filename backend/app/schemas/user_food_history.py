from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel, UUID4, Field, ConfigDict

class UserFoodHistoryBase(BaseModel):
    meal_datetime: datetime = Field(..., description="The datetime of the meal")
    meal_type: str = Field(..., description="The type of meal (breakfast, lunch, dinner, snack)")
    food_image_id: Optional[UUID4] = Field(None, description="Optional ID of the associated food image")
    total_nutrients: Dict[str, float] = Field(..., description="Total nutrients for the meal")

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )

class UserFoodHistoryCreate(UserFoodHistoryBase):
    pass

class UserFoodHistoryUpdate(UserFoodHistoryBase):
    pass

class UserFoodHistoryInDBBase(UserFoodHistoryBase):
    id: UUID4
    user_id: UUID4
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )

class UserFoodHistory(UserFoodHistoryInDBBase):
    pass 