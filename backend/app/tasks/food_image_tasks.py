from celery import Task
from app.core.celery_app import celery_app
from app.services.food_image_service import FoodImageService
from app.services.nutrient_estimation import NutrientEstimationService
from openai import AsyncOpenAI
from app.core.config import settings
import logging
import asyncio
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class FoodImageTask(Task):
    """Base task class with error handling and retry logic."""
    max_retries = 3
    default_retry_delay = 60  # 1 minute

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure."""
        logger.error(f"Task {task_id} failed: {str(exc)}")
        super().on_failure(exc, task_id, args, kwargs, einfo)

@celery_app.task(name="process_food_image", base=FoodImageTask, bind=True)
def process_food_image_task(self, image_id: str) -> Dict[str, Any]:
    """
    Process a food image through the recognition and nutrient estimation pipeline.
    
    Args:
        image_id: The ID of the uploaded food image
        
    Returns:
        Dictionary containing the processing results
    """
    try:
        # Initialize services
        openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        food_image_service = FoodImageService(openai_client)
        nutrient_service = NutrientEstimationService(openai_client)
        
        # Run the async functions in an event loop
        loop = asyncio.get_event_loop()
        
        # Step 1: Get food recognition results
        recognition_results = loop.run_until_complete(
            food_image_service.process_image(image_id)
        )
        
        if not recognition_results or not recognition_results.get("food_items"):
            return {
                "status": "error",
                "error": "No food items recognized in the image"
            }
        
        # Step 2: Estimate nutrients for recognized foods
        food_items = recognition_results["food_items"]
        nutrient_results = loop.run_until_complete(
            nutrient_service.estimate_nutrients(food_items)
        )
        
        # Step 3: Combine and return results
        return {
            "status": "success",
            "image_id": image_id,
            "recognition_results": recognition_results,
            "nutrient_results": nutrient_results
        }
        
    except Exception as e:
        logger.error(f"Error processing food image {image_id}: {str(e)}")
        # Retry the task
        raise self.retry(exc=e)

@celery_app.task(name="get_task_status")
def get_task_status(task_id: str) -> Dict[str, Any]:
    """
    Get the status of a Celery task.
    
    Args:
        task_id: The ID of the Celery task
        
    Returns:
        Dictionary containing the task status and results if available
    """
    task = celery_app.AsyncResult(task_id)
    
    if task.ready():
        if task.successful():
            return {
                "task_id": task_id,
                "status": "completed",
                "result": task.result
            }
        else:
            return {
                "task_id": task_id,
                "status": "failed",
                "error": str(task.result)
            }
    
    return {
        "task_id": task_id,
        "status": "processing"
    } 