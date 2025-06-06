from sqlalchemy.orm import Session
from backend.app.db.base_class import Base
from backend.app.db.session import engine
from backend.app.models.receipt import Receipt, LineItem
from backend.app.models.models import User, NutrientLedger
from backend.app.core.config import settings

def init_db() -> None:
    # Create all tables
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    print("Creating initial data")
    init_db()
    print("Initial data created") 