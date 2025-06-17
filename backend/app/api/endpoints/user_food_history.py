from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import user_food_history as crud
from app.schemas.user_food_history import (
    UserFoodHistory,
    UserFoodHistoryCreate,
    UserFoodHistoryUpdate,
)

router = APIRouter()

@router.post("/", response_model=UserFoodHistory)
def create_food_history(
    *,
    db: Session = Depends(deps.get_db),
    food_history_in: UserFoodHistoryCreate,
    current_user = Depends(deps.get_current_user),
) -> UserFoodHistory:
    """
    Create new food history entry.
    """
    print(f"[create_food_history API] DB session ID: {id(db)}")
    print(f"[create_food_history API] Current user ID: {current_user.id}")
    return crud.create_user_food_history(
        db=db, obj_in=food_history_in, user_id=current_user.id
    )

@router.get("/", response_model=List[UserFoodHistory])
def read_food_history(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user = Depends(deps.get_current_user),
) -> List[UserFoodHistory]:
    """
    Retrieve food history entries.
    """
    print(f"[read_food_history API] DB session ID: {id(db)}")
    print(f"[read_food_history API] Current user ID: {current_user.id}")
    if start_date and end_date:
        return crud.get_user_food_history_by_date_range(
            db=db, user_id=current_user.id, start_date=start_date, end_date=end_date
        )
    return crud.get_user_food_history(
        db=db, user_id=current_user.id, skip=skip, limit=limit
    )

@router.get("/{history_id}", response_model=UserFoodHistory)
def read_food_history_by_id(
    history_id: str,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
) -> UserFoodHistory:
    """
    Get specific food history entry by ID.
    """
    print(f"[read_food_history_by_id API] DB session ID: {id(db)}")
    print(f"[read_food_history_by_id API] Current user ID: {current_user.id}")
    food_history = crud.get_user_food_history_by_id(
        db=db, user_id=current_user.id, history_id=history_id
    )
    if not food_history:
        raise HTTPException(status_code=404, detail="Food history not found")
    return food_history 