import pytest
from datetime import datetime
from uuid import uuid4, UUID
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user_food_history import UserFoodHistory
from app.schemas.user_food_history import UserFoodHistoryCreate
from app.models.models import FoodImage
from app.models.user import User
from app.crud import user_food_history as crud
from app.services.user_service import get_password_hash
from app.api import deps

# Test data
test_user_id = UUID("bce6bd0f-22fc-4183-a2f4-fe2e14bb04a5")
test_food_image_id = UUID("b713dae6-1b08-4262-9795-b400269cabcf")
test_meal_type = "lunch"
test_total_nutrients = {"calories": 500.0, "protein": 30.0, "carbs": 50.0, "fat": 20.0}
test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiY2U2YmQwZi0yMmZjLTQxODMtYTJmNC1mZTJlMTRiYjA0YTUiLCJleHAiOjE3NDA5MjQwMDB9.8Q5YwXZQZQZQZQZQZQZQZQZQZQZQZQZQZQZQZQZQZQ"
test_meal_datetime = datetime(2025, 6, 14, 19, 59, 43, 376889)

@pytest.fixture
def test_user(db_session: Session):
    print(f"[test_user fixture] db_session ID: {id(db_session)}")
    hashed_password = get_password_hash("testpassword")
    user = User(
        id=test_user_id,
        email="test@example.com",
        hashed_password=hashed_password,
        demographics={},
        settings={},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        last_login=datetime.utcnow()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    print(f"[test_user fixture] User created with ID: {user.id}")
    return user

@pytest.fixture
def test_food_image(db_session: Session, test_user: User):
    print(f"[test_food_image fixture] db_session ID: {id(db_session)}")
    food_image = FoodImage(
        id=test_food_image_id,
        user_id=test_user.id,
        image_url="https://example.com/test.jpg",
        captured_at=datetime.utcnow(),
        status="processed",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(food_image)
    db_session.commit()
    db_session.refresh(food_image)
    print(f"[test_food_image fixture] FoodImage created with ID: {food_image.id}, user_id: {food_image.user_id}")
    return food_image

@pytest.fixture
def test_food_history(db_session: Session, test_food_image: FoodImage, test_user: User):
    food_history_in = UserFoodHistoryCreate(
        meal_datetime=test_meal_datetime.isoformat(),
        meal_type=test_meal_type,
        food_image_id=test_food_image_id,
        total_nutrients=test_total_nutrients
    )
    food_history = crud.create_user_food_history(db=db_session, obj_in=food_history_in, user_id=test_user.id)
    db_session.commit()
    db_session.refresh(food_history)
    return food_history

def test_create_food_history(client_with_db: TestClient, db_session: Session, test_user: User, test_food_image: FoodImage):
    print(f"[test_create_food_history] test_user_id: {test_user.id}")
    print(f"[test_create_food_history] test_food_image_id: {test_food_image_id}")
    print(f"[test_create_food_history] test_token: {test_token}")
    print(f"[test_create_food_history] db_session ID: {id(db_session)}")

    # Explicitly set overrides within the test function to ensure the correct session and user are used
    from app.main import app
    app.dependency_overrides[deps.get_db] = lambda: db_session
    app.dependency_overrides[deps.get_current_user] = lambda: test_user

    food_history_in = UserFoodHistoryCreate(
        meal_datetime=test_meal_datetime.isoformat(),
        meal_type=test_meal_type,
        food_image_id=test_food_image_id,
        total_nutrients=test_total_nutrients
    )
    data = food_history_in.model_dump()
    data["meal_datetime"] = test_meal_datetime.isoformat()
    data["food_image_id"] = str(test_food_image_id)
    print(f"[test_create_food_history] Request data: {data}")
    response = client_with_db.post(
        "/api/v1/food-history/",
        json=data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    content = response.json()
    assert content["meal_type"] == test_meal_type
    assert content["food_image_id"] == str(test_food_image_id)
    assert content["total_nutrients"] == test_total_nutrients
    
    # Clean up overrides after the test
    app.dependency_overrides.pop(deps.get_db, None)
    app.dependency_overrides.pop(deps.get_current_user, None)

def test_read_food_history(client_with_db: TestClient, db_session: Session, test_user: User, test_food_history: UserFoodHistory):
    from app.main import app
    app.dependency_overrides[deps.get_db] = lambda: db_session
    app.dependency_overrides[deps.get_current_user] = lambda: test_user
    response = client_with_db.get(
        "/api/v1/food-history/",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content) > 0
    assert content[0]["meal_type"] == test_meal_type
    assert content[0]["food_image_id"] == str(test_food_image_id)
    app.dependency_overrides.pop(deps.get_db, None)
    app.dependency_overrides.pop(deps.get_current_user, None)

def test_read_food_history_by_id(client_with_db: TestClient, db_session: Session, test_user: User, test_food_history: UserFoodHistory):
    from app.main import app
    app.dependency_overrides[deps.get_db] = lambda: db_session
    app.dependency_overrides[deps.get_current_user] = lambda: test_user
    response = client_with_db.get(
        f"/api/v1/food-history/{test_food_history.id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    content = response.json()
    assert content["meal_type"] == test_meal_type
    assert content["food_image_id"] == str(test_food_image_id)
    assert content["total_nutrients"] == test_total_nutrients
    app.dependency_overrides.pop(deps.get_db, None)
    app.dependency_overrides.pop(deps.get_current_user, None) 