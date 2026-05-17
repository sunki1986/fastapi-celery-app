import time
from .celery_worker import celery_app

@celery_app.task(name='tasks.heavy_computation')
def heavy_computation(duration):
    time.sleep(duration)
    return f'Heavy computation completed after {duration} seconds'
    