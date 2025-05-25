from datetime import datetime
from typing import Dict, Optional
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.base_class import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    version = Column(Integer, nullable=False, default=1)
    demographics = Column(JSON, nullable=False)
    settings = Column(JSON, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    food_images = relationship("FoodImage", back_populates="user")
    nutrient_ledgers = relationship("NutrientLedger", back_populates="user")

    __table_args__ = (
        Index("idx_users_email", "email"),
    )

class FoodImage(Base):
    __tablename__ = "food_images"

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

    __table_args__ = (
        Index("idx_food_images_user_captured_at", "user_id", "captured_at"),
    )

class FoodItem(Base):
    __tablename__ = "food_items"

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

    __table_args__ = (
        Index("idx_food_items_fdc_id", "fdc_id"),
    )

class NutrientLedger(Base):
    __tablename__ = "nutrient_ledgers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    week_start = Column(DateTime, nullable=False)
    nutrient = Column(JSON, nullable=False)  # Stores nutrient values
    percent_rda = Column(JSON, nullable=False)  # Stores RDA percentages
    last_updated = Column(DateTime, nullable=False, default=datetime.utcnow)
    data_source = Column(String, nullable=False)  # image, manual, estimated

    # Relationships
    user = relationship("User", back_populates="nutrient_ledgers")

    __table_args__ = (
        Index("idx_nutrient_ledgers_user_week", "user_id", "week_start"),
    ) 