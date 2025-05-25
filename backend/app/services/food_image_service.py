import os
import uuid
import base64
from datetime import datetime
from typing import List, Optional, Tuple
from fastapi import UploadFile, HTTPException
from PIL import Image
import magic
from openai import AsyncOpenAI
from sqlalchemy.orm import Session
import shutil
from uuid import UUID

from app.core.config import settings
from app.models.models import FoodImage, FoodItem
from app.schemas.food_image import FoodImageCreate, FoodImageResponse

# Configure OpenAI
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

class FoodImageService:
    def __init__(self, db: Session):
        self.db = db
        self.allowed_mime_types = {
            'image/jpeg': '.jpg',
            'image/png': '.png',
            'image/heic': '.heic'
        }
        self.max_file_size = 10 * 1024 * 1024  # 10 MB

    async def validate_image(self, file: UploadFile) -> Tuple[bool, str]:
        """Validate image file type and size."""
        # Check file size
        file_size = 0
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset file pointer

        if file_size > self.max_file_size:
            return False, f"File size exceeds maximum limit of {self.max_file_size/1024/1024}MB"

        # Check file type
        content_type = magic.from_buffer(file.file.read(2048), mime=True)
        file.file.seek(0)  # Reset file pointer

        if content_type not in self.allowed_mime_types:
            return False, f"Unsupported file type: {content_type}. Allowed types: {', '.join(self.allowed_mime_types.keys())}"

        return True, ""

    async def save_image(self, file: UploadFile, user_id: UUID) -> str:
        """Save uploaded image to disk."""
        # Create user-specific directory
        upload_dir = os.path.join(settings.UPLOAD_DIR, str(user_id))
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        file_ext = os.path.splitext(file.filename)[1]
        filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(upload_dir, filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return file_path

    async def process_image_with_llm(self, image_path: str) -> List[dict]:
        """Process image using OpenAI's Vision API to identify food items."""
        try:
            # Read and encode image
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')

            # Check if API key is set
            if not settings.OPENAI_API_KEY:
                raise HTTPException(
                    status_code=500,
                    detail="OpenAI API key not configured"
                )

            # Call OpenAI API
            response = await client.chat.completions.create(
                model="gpt-4.1-nano", # don't change this, it's the only model that's affordable
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Identify all food items in this image. For each item, provide: 1) Description, 2) Quantity (as a number, e.g., 1, 2, 0.5), 3) Confidence (0-1). Format as JSON array with fields: description, quantity, confidence. Use numeric values only for quantity and confidence. Keep descriptions concise."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000  # Increased token limit
            )
            
            # Parse the response
            try:
                # Extract the content from the response
                content = response.choices[0].message.content
                
                # Clean up the content to ensure valid JSON
                content = content.strip()
                if not content.startswith('['):
                    content = '[' + content
                if not content.endswith(']'):
                    content = content + ']'
                
                # Parse the JSON array from the content
                import json
                food_items = json.loads(content)
                
                # Validate the structure of each food item
                validated_items = []
                for item in food_items:
                    # Handle both confidence and confidence_score fields
                    confidence = item.get("confidence", item.get("confidence_score", 0.0))
                    
                    # Convert quantity to float, defaulting to 1.0 if not a number
                    try:
                        quantity = float(item["quantity"])
                    except (ValueError, TypeError):
                        quantity = 1.0
                    
                    validated_items.append({
                        "description": item["description"],
                        "quantity": quantity,
                        "confidence": float(confidence),
                        "is_estimated": True
                    })
                
                return validated_items
                
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                # If parsing fails, log the error and return empty list
                print(f"Error parsing OpenAI response: {str(e)}")
                print(f"Raw response: {response.choices[0].message.content}")
                return []
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error processing image: {str(e)}"
            )

    async def create_food_image(self, user_id: str, file: UploadFile) -> FoodImageResponse:
        """Create a new food image record and process it."""
        # Validate image
        is_valid, error_msg = await self.validate_image(file)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)

        # Save image
        image_path = await self.save_image(file, user_id)

        # Create database record
        db_food_image = FoodImage(
            user_id=user_id,
            captured_at=datetime.utcnow(),
            image_url=image_path,
            status="processed",
            recognition_confidence=0.0  # Will be updated after processing
        )
        self.db.add(db_food_image)
        self.db.commit()
        self.db.refresh(db_food_image)

        # Process image with LLM
        food_items = await self.process_image_with_llm(image_path)

        # Create food item records
        for item in food_items:
            db_food_item = FoodItem(
                food_image_id=db_food_image.id,
                description=item["description"],
                quantity=item["quantity"],
                confidence=item["confidence"],
                is_estimated=True
            )
            self.db.add(db_food_item)

        self.db.commit()
        self.db.refresh(db_food_image)

        return FoodImageResponse.from_orm(db_food_image)

    def get_user_food_images(self, user_id: str, skip: int = 0, limit: int = 100) -> List[FoodImageResponse]:
        """Get all food images for a user."""
        food_images = self.db.query(FoodImage)\
            .filter(FoodImage.user_id == user_id)\
            .offset(skip)\
            .limit(limit)\
            .all()
        return [FoodImageResponse.from_orm(img) for img in food_images] 