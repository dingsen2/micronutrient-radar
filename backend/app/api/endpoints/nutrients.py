from typing import List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.services.nutrient_estimation import NutrientEstimationService, FoodItem, NutrientProfile
from app.core.deps import get_openai_client

router = APIRouter()

class NutrientEstimationRequest(BaseModel):
    food_items: List[FoodItem]

class NutrientEstimationResponse(BaseModel):
    food_items: List[dict]  # List of food items with their nutrient profiles

@router.post("/estimate", response_model=NutrientEstimationResponse)
async def estimate_nutrients(
    request: NutrientEstimationRequest,
    openai_client = Depends(get_openai_client)
):
    """
    Estimate nutrients for a list of food items.
    """
    try:
        # Initialize the service
        service = NutrientEstimationService(openai_client)
        
        # Get nutrient estimates
        results = await service.estimate_nutrients(request.food_items)
        
        # Format the response
        response_items = []
        for food_item, profile in results:
            if profile is None:
                # Skip items that failed estimation
                continue
                
            # Calculate total nutrients based on quantity
            total_nutrients = service.calculate_total_nutrients(food_item, profile)
            
            response_items.append({
                "food_item": food_item.dict(),
                "nutrient_profile": profile.dict(),
                "total_nutrients": total_nutrients
            })
        
        return NutrientEstimationResponse(food_items=response_items)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error estimating nutrients: {str(e)}"
        ) 