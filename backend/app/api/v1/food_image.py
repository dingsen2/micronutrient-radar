from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.models import User
from app.schemas.food_image import FoodImageResponse
from app.services.food_image_service import FoodImageService

router = APIRouter()

@router.post("/", response_model=FoodImageResponse)
async def create_food_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload and process a food image.
    """
    food_image_service = FoodImageService(db)
    return await food_image_service.create_food_image(current_user.id, file)

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