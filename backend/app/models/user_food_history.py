from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.user import User  # Import User from user.py
from app.models.models import FoodImage  # Import FoodImage from models.py

class UserFoodHistory(Base):
    __tablename__ = "user_food_history"
    __table_args__ = (
        Index("idx_user_food_history_user_meal", "user_id", "meal_datetime"),
        {'extend_existing': True}
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    meal_datetime = Column(DateTime, nullable=False)
    meal_type = Column(String, nullable=False)  # breakfast, lunch, dinner, snack
    food_image_id = Column(UUID(as_uuid=True), ForeignKey("food_images.id"), nullable=True)
    total_nutrients = Column(JSON, nullable=True)  # Store nutrient totals for the meal
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="food_history")
    food_image = relationship("FoodImage", back_populates="food_history")