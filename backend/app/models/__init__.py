from app.models.user import User
from app.models.user_food_history import UserFoodHistory
from app.models.models import FoodImage

# Import all models here to ensure they are registered with SQLAlchemy
__all__ = ["User", "UserFoodHistory", "FoodImage"] 