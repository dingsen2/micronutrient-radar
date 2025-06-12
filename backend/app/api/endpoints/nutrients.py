from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.services.nutrient_estimation import NutrientEstimationService, FoodItem, NutrientProfile
from app.core.deps import get_openai_client
from app.tasks.nutrient_tasks import estimate_nutrients_task # Import the Celery task
from app.core.celery_app import celery_app # Import the Celery app instance

router = APIRouter()

class NutrientEstimationRequest(BaseModel):
    food_items: List[FoodItem]

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@router.post("/estimate", response_model=TaskStatusResponse)
async def estimate_nutrients_async(
    request: NutrientEstimationRequest,
):
    """
    Initiate a Celery task to estimate nutrients for a list of food items.
    """
    try:
        # Directly call the Celery task and return its ID
        task = estimate_nutrients_task.delay([item.model_dump() for item in request.food_items])
        return TaskStatusResponse(task_id=task.id, status="processing", message="Nutrient estimation started.")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error initiating nutrient estimation task: {str(e)}"
        )

@router.get("/task/{task_id}", response_model=TaskStatusResponse)
async def get_nutrient_estimation_task_status(task_id: str):
    """
    Get the status and result of a nutrient estimation task.
    """
    task = celery_app.AsyncResult(task_id)

    if task.ready():
        if task.successful():
            return TaskStatusResponse(
                task_id=task_id,
                status="completed",
                result=task.result # The result from the Celery task
            )
        else:
            return TaskStatusResponse(
                task_id=task_id,
                status="failed",
                error=str(task.result) # The error from the Celery task
            )
    else:
        return TaskStatusResponse(
            task_id=task_id,
            status="processing"
        ) 