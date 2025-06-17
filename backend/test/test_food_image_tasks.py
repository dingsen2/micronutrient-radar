import pytest
from unittest.mock import patch, AsyncMock
from app.tasks.food_image_tasks import process_food_image_task, get_task_status

@pytest.fixture
def mock_food_image_service():
    with patch('app.tasks.food_image_tasks.FoodImageService') as mock:
        mock_instance = AsyncMock()
        mock.return_value = mock_instance
        yield mock_instance

def test_process_food_image_task_success(mock_food_image_service):
    # Mock successful food recognition
    mock_food_image_service.process_food_image.return_value = {
        "food_items": [
            {
                "description": "apple",
                "quantity": 1,
                "unit": "piece",
                "confidence": 0.9,
                "is_estimated": True
            }
        ],
        "status": "processed",
        "recognition_confidence": 0.9
    }
    
    # Run the task
    result = process_food_image_task("test-image-id")
    
    # Verify success
    assert result["status"] == "success"
    assert result["image_id"] == "test-image-id"
    assert "recognition_results" in result
    assert result["recognition_results"]["food_items"][0]["description"] == "apple"
    mock_food_image_service.process_food_image.assert_called_once_with("test-image-id")

def test_process_food_image_task_no_items(mock_food_image_service):
    # Mock empty food recognition results
    mock_food_image_service.process_food_image.return_value = {
        "food_items": [],
        "status": "processed",
        "recognition_confidence": 0.0
    }
    
    # Run the task
    result = process_food_image_task("test-image-id")
    
    # Verify error handling
    assert result["status"] == "success"
    assert result["image_id"] == "test-image-id"
    assert "recognition_results" in result
    assert result["recognition_results"]["food_items"] == []

def test_process_food_image_task_error(mock_food_image_service):
    # Mock service to raise an exception
    mock_food_image_service.process_food_image.side_effect = Exception("API Error")
    
    # Run the task and expect it to retry
    with pytest.raises(Exception) as exc_info:
        process_food_image_task("test-image-id")
    assert str(exc_info.value) == "API Error"

def test_get_task_status():
    # Test task status retrieval
    with patch('app.tasks.food_image_tasks.celery_app.AsyncResult') as mock_async_result:
        # Mock a completed task
        mock_result = mock_async_result.return_value
        mock_result.ready.return_value = True
        mock_result.successful.return_value = True
        mock_result.result = {"status": "success"}

        result = get_task_status("test-task-id")
        assert result["status"] == "completed"
        assert result["result"] == {"status": "success"} 