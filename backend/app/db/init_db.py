from sqlalchemy.orm import Session
from app.db.session import engine
from app.db.base_class import Base
from app.models.models import User
from app.models.models import FoodImage, FoodItem
from app.models.models import NutrientLedger

def init_db() -> None:
    # Create all tables
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    print("Creating initial data")
    init_db()
    print("Initial data created") 