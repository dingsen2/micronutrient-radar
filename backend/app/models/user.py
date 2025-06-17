from datetime import datetime
from sqlalchemy import Column, String, Integer, JSON, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.db.base_class import Base

class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        Index("idx_users_email", "email"),
        {'extend_existing': True}
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    version = Column(Integer, nullable=False, default=1)
    demographics = Column(JSON, nullable=False)  # {age_range, sex, diet_style}
    settings = Column(JSON, nullable=False)  # {ocr_offline: bool, units: metric|imperial}
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    food_images = relationship("FoodImage", back_populates="user")
    nutrient_ledgers = relationship("NutrientLedger", back_populates="user")
    food_history = relationship("UserFoodHistory", back_populates="user")