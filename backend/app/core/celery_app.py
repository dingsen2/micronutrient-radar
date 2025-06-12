from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "micronutrient",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.nutrient_tasks",
        "app.tasks.food_image_tasks"
    ]
)

# Optional configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    worker_prefetch_multiplier=1,  # Process one task at a time
    task_routes={
        "process_food_image": {"queue": "food_image"},
        "estimate_nutrients": {"queue": "nutrients"},
    },
    task_default_queue="default",
    task_queues={
        "default": {
            "exchange": "default",
            "routing_key": "default",
        },
        "food_image": {
            "exchange": "food_image",
            "routing_key": "food_image",
        },
        "nutrients": {
            "exchange": "nutrients",
            "routing_key": "nutrients",
        },
    }
) 