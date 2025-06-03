from sqlalchemy import Column, String, Float, Boolean, ForeignKey, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSON
import uuid
import enum
from .base import Base

class ReceiptStatus(str, enum.Enum):
    PARSED = "parsed"
    NEEDS_REVIEW = "needs_review"
    FAILED = "failed"

class OCRProvider(str, enum.Enum):
    LOCAL = "local"
    CLOUD = "cloud"

class Receipt(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    datetime = Column(DateTime, nullable=False, index=True)
    raw_text = Column(String, nullable=False)  # Encrypted in production
    status = Column(Enum(ReceiptStatus), nullable=False)
    ocr_confidence = Column(Float, nullable=True)
    ocr_provider = Column(Enum(OCRProvider), nullable=True)

class LineItem(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    receipt_id = Column(UUID(as_uuid=True), ForeignKey("receipt.id"), nullable=False, index=True)
    description = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    fdc_id = Column(String, nullable=True, index=True)  # USDA FoodData Central ID
    confidence = Column(Float, nullable=True)
    is_estimated = Column(Boolean, default=False) 