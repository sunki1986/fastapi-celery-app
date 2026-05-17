import os
from celery import Celery
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
celery_app = Celery("worker", broker=redis_url, backend=redis_url, imports=["app.tasks"])

celery_app.conf.update(
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    
    # CHANGE THIS: Time in seconds for results to stay in Redis
    result_expires=3600  # Results will now disappear after 1 hour (3600 seconds)
)