import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "backend",
    broker=redis_url,
    backend=redis_url,
    include=["backend.tasks"]
)

celery_app.conf.update(
    result_expires=3600,
    worker_concurrency=int(os.getenv("CELERY_WORKER_CONCURRENCY", "1")),
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

if __name__ == "__main__":
    celery_app.start()
