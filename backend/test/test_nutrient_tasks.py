import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.tasks.nutrient_tasks import estimate_nutrients_task
from app.services.nutrient_estimation import FoodItem, NutrientProfile
from datetime import datetime

@pytest.fixture
def mock_openai_client():
    with patch('app.tasks.nutrient_tasks.AsyncOpenAI') as mock:
        client = AsyncMock()
        mock.return_value = client
        yield client

@pytest.fixture
def sample_food_items():
    return [
        {
            "description": "1 medium apple",
            "quantity": 1.0,
            "unit": "piece",
            "confidence": 0.95,
            "is_estimated": True
        },
        {
            "description": "2 slices of bread",
            "quantity": 2.0,
            "unit": "piece",
            "confidence": 0.9,
            "is_estimated": True
        }
    ]

def test_estimate_nutrients_task_success(mock_openai_client, sample_food_items):
    # Mock the OpenAI response
    mock_response = AsyncMock()
    mock_response.choices = [
        AsyncMock(message=AsyncMock(function_call=AsyncMock(
            arguments='{"nutrients": {"iron_mg": 0.5, "potassium_mg": 100, "magnesium_mg": 10, "calcium_mg": 5, "vitamin_d_mcg": 0.1, "vitamin_b12_mcg": 0.01, "folate_mcg": 2, "zinc_mg": 0.2, "selenium_mcg": 1, "fiber_g": 2}}'
        )))
    ]
    mock_openai_client.chat.completions.create.return_value = mock_response

    # Run the task
    result = estimate_nutrients_task(sample_food_items)

    # Verify the result
    assert result["status"] == "success"
    assert len(result["results"]) == 2
    
    # Check first food item
    first_result = result["results"][0]
    assert first_result["food_item"]["description"] == "1 medium apple"
    assert first_result["nutrient_profile"] is not None
    assert "iron_mg" in first_result["nutrient_profile"]["nutrients"]
    assert "fiber_g" in first_result["nutrient_profile"]["nutrients"]

def test_estimate_nutrients_task_error(sample_food_items):
    # Patch the event loop to raise an exception when run_until_complete is called
    from unittest.mock import patch, MagicMock
    with patch('app.tasks.nutrient_tasks.asyncio.get_event_loop') as mock_get_event_loop:
        mock_loop = MagicMock()
        mock_loop.run_until_complete.side_effect = Exception("API Error")
        mock_get_event_loop.return_value = mock_loop
        result = estimate_nutrients_task(sample_food_items, openai_client=None)
    # Verify error handling
    assert result["status"] == "error"
    assert "error" in result
    assert "API Error" in result["error"] 