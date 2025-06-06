from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class FoodItem(BaseModel):
    description: str
    quantity: float
    unit: str
    confidence: float
    is_estimated: bool

class NutrientProfile(BaseModel):
    food_name: str
    nutrients: Dict[str, float]
    source: str
    llm_prompt_version: str
    estimated_by: str
    created_at: datetime
    updated_at: datetime

class NutrientEstimationRequest(BaseModel):
    food_items: List[FoodItem]

class NutrientEstimationResponse(BaseModel):
    task_id: Optional[str] = None
    status: str
    message: Optional[str] = None
    error: Optional[str] = None
    results: Optional[List[Dict[str, Any]]] = None
    food_items: List[Dict[str, Any]] = []

    class Config:
        from_attributes = True 