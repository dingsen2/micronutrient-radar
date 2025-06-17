import pytest
from datetime import datetime
from uuid import uuid4, UUID
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.models import FoodImage
from app.services.user_service import get_password_hash

# Test data (using dynamic UUIDs for better isolation)
test_user_id = uuid4()
test_food_image_id = uuid4()

@pytest.fixture
def basic_test_user(db_session: Session):
    hashed_password = get_password_hash("testpassword")
    user = User(
        id=test_user_id,
        email=f"test_basic_user_{uuid4()}@example.com", # Use unique email
        hashed_password=hashed_password,
        demographics={},
        settings={},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        last_login=datetime.utcnow()
    )
    db_session.add(user)
    db_session.commit() # Explicitly commit for this isolated test
    db_session.refresh(user)
    return user

@pytest.fixture
def basic_test_food_image(db_session: Session, basic_test_user: User):
    food_image = FoodImage(
        id=test_food_image_id,
        user_id=basic_test_user.id,
        image_url="https://example.com/basic_test.jpg",
        captured_at=datetime.utcnow(),
        status="processed",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(food_image)
    db_session.commit() # Explicitly commit for this isolated test
    db_session.refresh(food_image)
    return food_image

def test_basic_user_creation(db_session: Session, basic_test_user: User):
    retrieved_user = db_session.query(User).filter(User.id == basic_test_user.id).first()
    assert retrieved_user is not None
    assert retrieved_user.email == basic_test_user.email

def test_basic_food_image_creation(db_session: Session, basic_test_food_image: FoodImage):
    retrieved_image = db_session.query(FoodImage).filter(FoodImage.id == basic_test_food_image.id).first()
    assert retrieved_image is not None
    assert retrieved_image.user_id == basic_test_food_image.user_id 