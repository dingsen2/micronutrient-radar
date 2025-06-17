from datetime import datetime
from typing import Dict, Optional
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.base_class import Base
from app.models.user import User  # Import User from user.py

class FoodImage(Base):
    __tablename__ = "food_images"
    __table_args__ = (
        Index("idx_food_images_user_captured_at", "user_id", "captured_at"),
        {'extend_existing': True}
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    captured_at = Column(DateTime, nullable=False)
    image_url = Column(String, nullable=False)
    status = Column(String, nullable=False)  # processed, needs_review, failed
    recognition_confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="food_images")
    food_items = relationship("FoodItem", back_populates="food_image")
    food_history = relationship("UserFoodHistory", back_populates="food_image")

class FoodItem(Base):
    __tablename__ = "food_items"
    __table_args__ = (
        Index("idx_food_items_fdc_id", "fdc_id"),
        {'extend_existing': True}
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    food_image_id = Column(UUID(as_uuid=True), ForeignKey("food_images.id"), nullable=False)
    description = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    fdc_id = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    is_estimated = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    food_image = relationship("FoodImage", back_populates="food_items")

class NutrientLedger(Base):
    __tablename__ = "nutrient_ledgers"
    __table_args__ = (
        Index("idx_nutrient_ledgers_user_week", "user_id", "week_start"),
        {'extend_existing': True}
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    week_start = Column(DateTime, nullable=False)
    nutrient = Column(JSON, nullable=False)  # Stores nutrient values
    percent_rda = Column(JSON, nullable=False)  # Stores RDA percentages
    last_updated = Column(DateTime, nullable=False, default=datetime.utcnow)
    data_source = Column(String, nullable=False)  # image, manual, estimated

    # Relationships
    user = relationship("User", back_populates="nutrient_ledgers")