from app.core.celery_app import celery_app
from app.services.nutrient_estimation import NutrientEstimationService, FoodItem, NutrientProfile
from openai import AsyncOpenAI
from app.core.config import settings
import logging
import asyncio

logger = logging.getLogger(__name__)

@celery_app.task(name="estimate_nutrients")
def estimate_nutrients_task(food_items_data: list, openai_client=None, service=None) -> dict:
    """
    Celery task to estimate nutrients for a list of food items.
    
    Args:
        food_items_data: List of dictionaries containing food item data
        openai_client: Optional, injected OpenAI client for testing
        service: Optional, injected NutrientEstimationService for testing
        
    Returns:
        Dictionary containing the estimation results
    """
    try:
        # Initialize OpenAI client if not provided
        if openai_client is None:
            openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        # Initialize nutrient estimation service if not provided
        if service is None:
            service = NutrientEstimationService(openai_client)
        
        # Convert food items data to FoodItem objects
        food_items = [
            FoodItem(
                description=item["description"],
                quantity=item["quantity"],
                unit=item["unit"],
                confidence=item["confidence"],
                is_estimated=item["is_estimated"]
            )
            for item in food_items_data
        ]
        
        # Run the async function in an event loop
        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(service.estimate_nutrients(food_items))
        
        # Convert results to serializable format
        serialized_results = []
        for food_item, profile in results:
            if profile:
                serialized_results.append({
                    "food_item": food_item.model_dump(),
                    "nutrient_profile": profile.model_dump()
                })
            else:
                serialized_results.append({
                    "food_item": food_item.model_dump(),
                    "nutrient_profile": None
                })
        
        return {
            "status": "success",
            "results": serialized_results
        }
        
    except Exception as e:
        logger.error(f"Error in nutrient estimation task: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        } 