from celery import Celery
from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
from unittest.mock import patch, MagicMock
from pydantic import BaseModel

# Create Celery app
celery_app = Celery(
    'test_app',
    broker='redis://localhost:6379/1',
    backend='redis://localhost:6379/2'
)

# Define a simple task
@celery_app.task(name='test.add')
def add(x, y):
    return x + y

# Create FastAPI app
app = FastAPI()

class AddRequest(BaseModel):
    x: int
    y: int

@app.post("/add")
async def add_numbers(request: AddRequest):
    # Submit task to Celery
    task = add.delay(request.x, request.y)
    return {"task_id": task.id}

@app.get("/task/{task_id}")
async def get_task_status(task_id: str):
    task = add.AsyncResult(task_id, app=celery_app)
    if task.ready():
        if task.successful():
            return {"task_id": task_id, "status": "completed", "result": task.result}
        else:
            return {"task_id": task_id, "status": "failed", "error": str(task.result)}
    return {"task_id": task_id, "status": "processing"}

# Tests
@pytest.fixture
def client():
    return TestClient(app)

def test_add_numbers(client):
    with patch('test_celery_example.add.delay') as mock_delay:
        # Configure mock
        mock_task = MagicMock()
        mock_task.id = 'test-task-id'
        mock_delay.return_value = mock_task

        # Test endpoint
        response = client.post("/add", json={"x": 2, "y": 3})
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "test-task-id"
        mock_delay.assert_called_once_with(2, 3)

def test_get_task_status(client):
    with patch('test_celery_example.add.AsyncResult') as mock_async_result:
        # Configure mock for completed task
        mock_task = MagicMock()
        mock_task.ready.return_value = True
        mock_task.successful.return_value = True
        mock_task.result = 5
        mock_async_result.return_value = mock_task

        # Test endpoint
        response = client.get("/task/test-task-id")
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "test-task-id"
        assert data["status"] == "completed"
        assert data["result"] == 5 