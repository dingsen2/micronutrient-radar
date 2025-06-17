from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.user_food_history import UserFoodHistory
from app.schemas.user_food_history import UserFoodHistoryCreate, UserFoodHistoryUpdate

def create_user_food_history(
    db: Session, *, obj_in: UserFoodHistoryCreate, user_id: str
) -> UserFoodHistory:
    db_obj = UserFoodHistory(
        user_id=user_id,
        meal_datetime=obj_in.meal_datetime,
        meal_type=obj_in.meal_type,
        food_image_id=obj_in.food_image_id,
        total_nutrients=obj_in.total_nutrients,
    )
    db.add(db_obj)
    db.flush()
    return db_obj

def get_user_food_history(
    db: Session, user_id: str, skip: int = 0, limit: int = 100
) -> List[UserFoodHistory]:
    return (
        db.query(UserFoodHistory)
        .filter(UserFoodHistory.user_id == user_id)
        .order_by(UserFoodHistory.meal_datetime.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_user_food_history_by_date_range(
    db: Session, user_id: str, start_date: datetime, end_date: datetime
) -> List[UserFoodHistory]:
    return (
        db.query(UserFoodHistory)
        .filter(
            and_(
                UserFoodHistory.user_id == user_id,
                UserFoodHistory.meal_datetime >= start_date,
                UserFoodHistory.meal_datetime <= end_date
            )
        )
        .order_by(UserFoodHistory.meal_datetime.desc())
        .all()
    )

def get_user_food_history_by_id(
    db: Session, user_id: str, history_id: str
) -> Optional[UserFoodHistory]:
    return (
        db.query(UserFoodHistory)
        .filter(
            and_(
                UserFoodHistory.id == history_id,
                UserFoodHistory.user_id == user_id
            )
        )
        .first()
    ) 