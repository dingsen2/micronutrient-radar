import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from backend.app.tasks.food_image_tasks import process_food_image_task, get_task_status
from backend.app.core.celery_app import celery_app

@pytest.fixture
def mock_openai_client():
    with patch('backend.app.tasks.food_image_tasks.AsyncOpenAI') as mock:
        client = AsyncMock()
        mock.return_value = client
        yield client

@pytest.fixture
def mock_food_image_service():
    with patch('backend.app.tasks.food_image_tasks.FoodImageService') as mock:
        service = AsyncMock()
        mock.return_value = service
        yield service

@pytest.fixture
def mock_nutrient_service():
    with patch('backend.app.tasks.food_image_tasks.NutrientEstimationService') as mock:
        service = AsyncMock()
        mock.return_value = service
        yield service

def test_process_food_image_task_success(mock_food_image_service, mock_nutrient_service):
    # Mock food recognition results
    mock_food_image_service.process_image.return_value = {
        "food_items": [
            {
                "description": "apple",
                "quantity": 1,
                "unit": "piece",
                "confidence": 0.9,
                "is_estimated": True
            }
        ]
    }
    
    # Mock nutrient estimation results
    mock_nutrient_service.estimate_nutrients.return_value = [
        (
            {"description": "apple", "quantity": 1},
            {"nutrients": {"iron_mg": 0.5, "vitamin_c_mg": 10}}
        )
    ]
    
    # Run the task
    result = process_food_image_task("test-image-id")
    
    # Verify the result
    assert result["status"] == "success"
    assert result["image_id"] == "test-image-id"
    assert "recognition_results" in result
    assert "nutrient_results" in result
    assert len(result["recognition_results"]["food_items"]) == 1
    assert len(result["nutrient_results"]) == 1

def test_process_food_image_task_no_items(mock_food_image_service):
    # Mock empty food recognition results
    mock_food_image_service.process_image.return_value = {
        "food_items": []
    }
    
    # Run the task
    result = process_food_image_task("test-image-id")
    
    # Verify error handling
    assert result["status"] == "error"
    assert "No food items recognized" in result["error"]

def test_process_food_image_task_error(mock_food_image_service):
    # Mock service to raise an exception
    mock_food_image_service.process_image.side_effect = Exception("API Error")
    
    # Run the task and expect it to retry
    with pytest.raises(Exception) as exc_info:
        process_food_image_task("test-image-id")
    
    assert "API Error" in str(exc_info.value)

def test_get_task_status():
    # Mock Celery task
    mock_task = MagicMock()
    mock_task.ready.return_value = True
    mock_task.successful.return_value = True
    mock_task.result = {"status": "success", "data": "test"}
    
    with patch('backend.app.tasks.food_image_tasks.celery_app.AsyncResult') as mock_async_result:
        mock_async_result.return_value = mock_task
        
        # Test completed task
        result = get_task_status("test-task-id")
        assert result["status"] == "completed"
        assert result["result"] == {"status": "success", "data": "test"}
        
        # Test failed task
        mock_task.successful.return_value = False
        mock_task.result = "Task failed"
        result = get_task_status("test-task-id")
        assert result["status"] == "failed"
        assert result["error"] == "Task failed"
        
        # Test processing task
        mock_task.ready.return_value = False
        result = get_task_status("test-task-id")
        assert result["status"] == "processing" 