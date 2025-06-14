from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.models import User
from app.schemas.food_image import FoodImageResponse
from app.services.food_image_service import FoodImageService
from app.tasks.food_image_tasks import process_food_image_task, get_task_status

router = APIRouter()

@router.post("/", response_model=FoodImageResponse)
async def create_food_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a food image and start processing it in the background.
    Returns immediately with the image ID and a task ID for tracking processing status.
    """
    food_image_service = FoodImageService(db)
    food_image = await food_image_service.create_food_image(current_user.id, file)
    
    # Start Celery task for processing
    task = process_food_image_task.delay(str(food_image.id))
    
    # Add task ID to response
    response = FoodImageResponse.from_orm(food_image)
    response.task_id = task.id
    return response

@router.get("/task/{task_id}")
async def get_task_status_endpoint(task_id: str):
    """
    Get the status of a food image processing task.
    """
    return get_task_status(task_id)

@router.get("/", response_model=List[FoodImageResponse])
async def list_food_images(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all food images for the current user.
    """
    food_image_service = FoodImageService(db)
    return food_image_service.get_user_food_images(current_user.id, skip, limit) 