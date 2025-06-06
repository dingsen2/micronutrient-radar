from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.api.endpoints import nutrients
from backend.app.models.models import User
from datetime import datetime

@pytest.fixture
def mock_current_user():
    return User(
        id=1,
        email="test@example.com",
        hashed_password="hashed_password",
        version=1,
        demographics={},
        settings={},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        last_login=None
    )

@pytest.fixture
def client(mock_current_user):
    app.dependency_overrides[nutrients.get_current_user] = lambda: mock_current_user
    return TestClient(app, raise_server_exceptions=False)

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
    with patch('app.api.endpoints.nutrients.estimate_nutrients_task.delay') as mock_delay:
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
        assert "message" in data
        mock_delay.assert_called_once()

def test_get_task_status_processing(client):
    with patch('app.api.endpoints.nutrients.estimate_nutrients_task.AsyncResult') as mock_async_result:
        mock_task = MagicMock()
        mock_task.ready.return_value = False
        mock_async_result.return_value = mock_task
        response = client.get("/api/v1/nutrients/task/test-task-id")
        if response.status_code != 200:
            print("Response content:", response.content)
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "test-task-id"
        assert data["status"] == "processing"

def test_get_task_status_completed(client):
    with patch('app.api.endpoints.nutrients.estimate_nutrients_task.AsyncResult') as mock_async_result:
        mock_task = MagicMock()
        mock_task.ready.return_value = True
        mock_task.successful.return_value = True
        mock_task.result = {"status": "success", "results": [{"food_name": "apple", "nutrients": {"calories": 95}}]}
        mock_async_result.return_value = mock_task
        response = client.get("/api/v1/nutrients/task/test-task-id")
        if response.status_code != 200:
            print("Response content:", response.content)
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "test-task-id"
        assert data["status"] == "completed"
        assert "results" in data

def test_get_task_status_failed(client):
    with patch('app.api.endpoints.nutrients.estimate_nutrients_task.AsyncResult') as mock_async_result:
        mock_task = MagicMock()
        mock_task.ready.return_value = True
        mock_task.successful.return_value = False
        mock_task.result = Exception("Some error")
        mock_async_result.return_value = mock_task
        response = client.get("/api/v1/nutrients/task/test-task-id")
        if response.status_code != 200:
            print("Response content:", response.content)
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "test-task-id"
        assert data["status"] == "failed"
        assert "error" in data 