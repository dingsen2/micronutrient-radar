from typing import Dict, List, Optional, Tuple
import json
from datetime import datetime
import logging
from pydantic import BaseModel
import redis
from backend.app.core.deps import get_openai_client
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

class NutrientProfile(BaseModel):
    """Represents the nutrient profile of a food item."""
    food_name: str
    nutrients: Dict[str, float]  # e.g., {"iron_mg": 0.8, "potassium_mg": 350}
    source: str  # "model_estimate" or "cache"
    llm_prompt_version: str
    estimated_by: str
    created_at: datetime
    updated_at: datetime

class FoodItem(BaseModel):
    """Represents a food item from image recognition."""
    description: str
    quantity: float
    unit: str  # e.g., "lb", "g", "piece"
    confidence: float
    is_estimated: bool

class NutrientEstimationService:
    """Service for estimating nutrient content of food items using LLM."""
    
    def __init__(self, openai_client, redis_url: str = "redis://localhost:6379/0"):
        self.openai_client = openai_client
        self.redis_client = redis.Redis.from_url(redis_url)
        self.required_nutrients = [
            "iron_mg", "potassium_mg", "magnesium_mg", "calcium_mg",
            "vitamin_d_mcg", "vitamin_b12_mcg", "folate_mcg",
            "zinc_mg", "selenium_mcg", "fiber_g"
        ]

    async def estimate_nutrients(self, food_items: List[FoodItem]) -> List[Tuple[FoodItem, NutrientProfile]]:
        """
        Estimate nutrients for a list of food items.
        Returns a list of tuples containing the food item and its nutrient profile.
        """
        results = []
        
        for food_item in food_items:
            try:
                # Check cache first
                cached_profile = self._get_from_cache(food_item.description)
                if cached_profile:
                    results.append((food_item, cached_profile))
                    continue

                # Get nutrient estimation from LLM
                nutrient_profile = await self._get_llm_estimation(food_item)
                
                # Cache the result
                self._add_to_cache(food_item.description, nutrient_profile)
                
                results.append((food_item, nutrient_profile))
                
            except Exception as e:
                logger.error(f"Error estimating nutrients for {food_item.description}: {str(e)}")
                # Return None for failed items
                results.append((food_item, None))
        
        return results

    def _get_from_cache(self, food_name: str) -> Optional[NutrientProfile]:
        """Get nutrient profile from Redis cache."""
        try:
            cached_data = self.redis_client.get(food_name.lower())
            if cached_data:
                data = json.loads(cached_data)
                return NutrientProfile(**data)
        except Exception as e:
            logger.error(f"Error retrieving from cache: {str(e)}")
        return None

    def _add_to_cache(self, food_name: str, profile: NutrientProfile):
        """Add nutrient profile to Redis cache."""
        try:
            self.redis_client.set(food_name.lower(), profile.model_dump_json())
        except Exception as e:
            logger.error(f"Error adding to cache: {str(e)}")

    async def _get_llm_estimation(self, food_item: FoodItem) -> NutrientProfile:
        """
        Get nutrient estimation from LLM.
        Uses function calling to get structured output.
        """
        # Prepare the prompt for nutrient estimation
        prompt = f"""Estimate the nutrient content per {food_item.unit} for {food_item.description}.
        Return the values in the following format:
        - iron_mg: milligrams of iron
        - potassium_mg: milligrams of potassium
        - magnesium_mg: milligrams of magnesium
        - calcium_mg: milligrams of calcium
        - vitamin_d_mcg: micrograms of vitamin D
        - vitamin_b12_mcg: micrograms of vitamin B12
        - folate_mcg: micrograms of folate
        - zinc_mg: milligrams of zinc
        - selenium_mcg: micrograms of selenium
        - fiber_g: grams of fiber"""

        # Define the function schema for structured output
        function_schema = {
            "name": "get_nutrient_profile",
            "description": "Get nutrient profile for a food item",
            "parameters": {
                "type": "object",
                "properties": {
                    "nutrients": {
                        "type": "object",
                        "properties": {
                            nutrient: {"type": "number"} for nutrient in self.required_nutrients
                        },
                        "required": self.required_nutrients
                    }
                },
                "required": ["nutrients"]
            }
        }

        # Call OpenAI with function calling
        response = await self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            functions=[function_schema],
            function_call={"name": "get_nutrient_profile"}
        )

        # Parse the response
        function_response = json.loads(response.choices[0].message.function_call.arguments)
        
        # Create and return the nutrient profile
        return NutrientProfile(
            food_name=food_item.description,
            nutrients=function_response["nutrients"],
            source="model_estimate",
            llm_prompt_version="v1.0",
            estimated_by="gpt-4",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

    def calculate_total_nutrients(self, food_item: FoodItem, profile: NutrientProfile) -> Dict[str, float]:
        """
        Calculate total nutrients based on quantity and unit.
        Returns nutrient values adjusted for the actual quantity.
        """
        # Convert to grams for calculation
        quantity_in_grams = self._convert_to_grams(food_item.quantity, food_item.unit)
        
        # Calculate total nutrients
        total_nutrients = {}
        for nutrient, value in profile.nutrients.items():
            # Convert per 100g values to actual quantity
            total_nutrients[nutrient] = (value * quantity_in_grams) / 100
        
        return total_nutrients

    def _convert_to_grams(self, quantity: float, unit: str) -> float:
        """
        Convert various units to grams for consistent calculation.
        """
        unit = unit.lower()
        if unit == "g":
            return quantity
        elif unit == "kg":
            return quantity * 1000
        elif unit == "lb":
            return quantity * 453.592
        elif unit == "oz":
            return quantity * 28.3495
        elif unit == "piece":
            # Use average weights for common items
            # This should be expanded based on your needs
            return quantity * 100  # Default to 100g per piece
        else:
            raise ValueError(f"Unsupported unit: {unit}") 