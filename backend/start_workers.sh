#!/bin/bash

# Start Celery worker for food image processing
celery -A app.core.celery_app worker -Q food_image -n food_image_worker@%h -l info &

# Start Celery worker for nutrient estimation
celery -A app.core.celery_app worker -Q nutrients -n nutrient_worker@%h -l info &

# Start Celery worker for default tasks
celery -A app.core.celery_app worker -Q default -n default_worker@%h -l info &

# Start Flower for monitoring
celery -A app.core.celery_app flower --port=5555 &

echo "All Celery workers and Flower started. Press Ctrl+C to stop all processes."
wait 