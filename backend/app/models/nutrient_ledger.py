from sqlalchemy import Column, String, Float, ForeignKey, Enum, Date
from sqlalchemy.dialects.postgresql import UUID, JSON
import uuid
import enum
from .base import Base

class DataSource(str, enum.Enum):
    RECEIPT = "receipt"
    MANUAL = "manual"
    ESTIMATED = "estimated"

class NutrientLedger(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False, index=True)
    week_start = Column(Date, nullable=False, index=True)
    nutrient = Column(JSON, nullable=False)  # {iron: mg, potassium: mg, ...}
    percent_rda = Column(JSON, nullable=False)  # {iron: %, ...}
    data_source = Column(Enum(DataSource), nullable=False) 