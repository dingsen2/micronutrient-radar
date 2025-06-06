from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.receipt import Receipt, ReceiptStatus, OCRProvider
from backend.app.services.user_service import get_current_user
from backend.app.models.user import User
from backend.app.core.config import settings
from datetime import datetime
import uuid
import os
from typing import List
import shutil

router = APIRouter()

# Maximum file size (10MB)
MAX_FILE_SIZE = settings.MAX_UPLOAD_SIZE

# Allowed file types
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.pdf'}

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_receipt(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Validate file size
    file_size = 0
    chunk_size = 1024 * 1024  # 1MB chunks
    
    while chunk := await file.read(chunk_size):
        file_size += len(chunk)
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File size exceeds maximum limit of 10MB"
            )
    
    # Reset file pointer
    await file.seek(0)
    
    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Create receipt record
    receipt = Receipt(
        id=uuid.uuid4(),
        user_id=current_user.id,
        datetime=datetime.utcnow(),
        raw_text="",  # Will be populated after OCR
        status=ReceiptStatus.NEEDS_REVIEW,
        ocr_confidence=None,
        ocr_provider=None
    )
    
    # Save receipt to database
    db.add(receipt)
    db.commit()
    db.refresh(receipt)
    
    # Create user-specific directory if it doesn't exist
    user_dir = os.path.join(settings.UPLOAD_DIR, str(current_user.id))
    os.makedirs(user_dir, exist_ok=True)
    
    # Save file with receipt ID as filename
    file_path = os.path.join(user_dir, f"{receipt.id}{file_ext}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # TODO: Implement OCR processing
    # For now, just return the receipt ID
    return {"receipt_id": str(receipt.id)} 