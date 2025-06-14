from sqlalchemy import Column, String, Integer, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .base import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version = Column(Integer, nullable=False, default=1)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    demographics = Column(JSON, nullable=False)  # {age_range, sex, diet_style}
    settings = Column(JSON, nullable=False)  # {ocr_offline: bool, units: metric|imperial}
    last_login = Column(DateTime, nullable=True) 