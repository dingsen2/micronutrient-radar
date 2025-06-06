from typing import List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.app.services.nutrient_estimation import NutrientEstimationService, FoodItem, NutrientProfile
from backend.app.core.deps import get_openai_client
from backend.app.schemas.nutrient import NutrientEstimationRequest, NutrientEstimationResponse
from backend.app.tasks.nutrient_tasks import estimate_nutrients_task
from backend.app.api.deps import get_current_user
from backend.app.models.models import User

router = APIRouter()

@router.post("/estimate", response_model=NutrientEstimationResponse)
async def estimate_nutrients(
    request: NutrientEstimationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Estimate nutrients for a list of food items using Celery task.
    """
    try:
        # Convert food items to serializable format
        food_items_data = [
            {
                "description": item.description,
                "quantity": item.quantity,
                "unit": item.unit,
                "confidence": item.confidence,
                "is_estimated": item.is_estimated
            }
            for item in request.food_items
        ]
        
        # Submit task to Celery
        task = estimate_nutrients_task.delay(food_items_data)
        
        return {
            "task_id": task.id,
            "status": "processing",
            "message": "Nutrient estimation task has been queued",
            "food_items": []  # Return empty list for processing state
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error submitting nutrient estimation task: {str(e)}"
        )

@router.get("/task/{task_id}", response_model=NutrientEstimationResponse)
async def get_task_status(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get the status and results of a nutrient estimation task.
    """
    try:
        task = estimate_nutrients_task.AsyncResult(task_id)
        
        if task.ready():
            if task.successful():
                result = task.result
                if result["status"] == "error":
                    return {
                        "task_id": task_id,
                        "status": "failed",
                        "error": result.get("error", "Unknown error"),
                        "food_items": []  # Return empty list for error state
                    }
                return {
                    "task_id": task_id,
                    "status": "completed",
                    "results": result.get("results", []),
                    "food_items": result.get("results", [])  # Return results for completed state
                }
            else:
                return {
                    "task_id": task_id,
                    "status": "failed",
                    "error": str(task.result),
                    "food_items": []  # Return empty list for failed state
                }
        else:
            return {
                "task_id": task_id,
                "status": "processing",
                "message": "Task is still being processed",
                "food_items": []  # Return empty list for processing state
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving task status: {str(e)}"
        ) 