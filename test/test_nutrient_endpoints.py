from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.api.endpoints import nutrients
from backend.app.models.models import User
from datetime import datetime
from backend.app.core.celery_app import celery_app # Import the actual celery_app

@pytest.fixture
def mock_current_user():
    # In a real scenario, you might mock the User object with a proper schema if needed
    # For now, we'll return a minimal mock user to allow tests to proceed
    class MockUser:
        id = "bce6bd0f-22fc-4183-a2f4-fe2e14bb04a5" # Example UUID
        email = "test@example.com"
        # Add other necessary attributes if they are accessed by dependencies

    return MockUser()

@pytest.fixture
def client(client_with_db, mock_current_user):
    # from backend.app.api.endpoints import nutrients # Not needed here directly
    # The 'nutrients' router itself does not depend on 'get_current_user'
    # If other parts of the app tested by client_with_db need it, it should be set up globally or in specific tests.
    # app.dependency_overrides[nutrients.get_current_user] = lambda: mock_current_user # Removed this line
    yield client_with_db
    app.dependency_overrides.clear()

@pytest.fixture
def sample_food_items():
    return [
        {
            "description": "1 medium apple",
            "quantity": 1.0,
            "unit": "piece",
            "confidence": 0.95,
            "is_estimated": True
        }
    ]

def test_estimate_nutrients_endpoint(client, sample_food_items):
    with patch('backend.app.tasks.nutrient_tasks.estimate_nutrients_task.delay') as mock_delay:
        mock_task = MagicMock()
        mock_task.id = 'test-task-id'
        mock_delay.return_value = mock_task
        response = client.post(
            "/api/v1/nutrients/estimate",
            json={"food_items": sample_food_items}
        )
        if response.status_code != 200:
            print("Response content:", response.content)
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert data["status"] == "processing"
        mock_delay.assert_called_once()

def test_get_task_status_processing(client):
    with patch('backend.app.api.endpoints.nutrients.celery_app.AsyncResult') as mock_async_result:
        mock_task = MagicMock()
        mock_task.ready.return_value = False # Task is not ready yet
        mock_async_result.return_value = mock_task
        response = client.get("/api/v1/nutrients/task/test-task-id")
        if response.status_code != 200:
            print("Response content:", response.content)
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "test-task-id"
        assert data["status"] == "processing"

def test_get_task_status_completed(client):
    with patch('backend.app.api.endpoints.nutrients.celery_app.AsyncResult') as mock_async_result:
        mock_task = MagicMock()
        mock_task.ready.return_value = True # Task is ready
        mock_task.successful.return_value = True # Task was successful
        mock_task.result = {"status": "success", "results": [{"food_name": "apple", "nutrients": {"calories": 95}}]}
        mock_async_result.return_value = mock_task
        response = client.get("/api/v1/nutrients/task/test-task-id")
        if response.status_code != 200:
            print("Response content:", response.content)
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "test-task-id"
        assert data["status"] == "completed"
        assert "results" in data["result"]

def test_get_task_status_failed(client):
    with patch('backend.app.api.endpoints.nutrients.celery_app.AsyncResult') as mock_async_result:
        mock_task = MagicMock()
        mock_task.ready.return_value = True # Task is ready
        mock_task.successful.return_value = False # Task failed
        mock_task.result = "Some error" # The error message
        mock_async_result.return_value = mock_task
        response = client.get("/api/v1/nutrients/task/test-task-id")
        if response.status_code != 200:
            print("Response content:", response.content)
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "test-task-id"
        assert data["status"] == "failed"
        assert "error" in data 