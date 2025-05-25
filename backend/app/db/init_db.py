from sqlalchemy.orm import Session
from app.db.session import engine
from app.models.base import Base
from app.models.user import User
from app.models.receipt import Receipt, LineItem
from app.models.nutrient_ledger import NutrientLedger

def init_db() -> None:
    # Create all tables
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    print("Creating initial data")
    init_db()
    print("Initial data created") 