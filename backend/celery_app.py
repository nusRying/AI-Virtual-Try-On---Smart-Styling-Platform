import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
# Force mock_redis for local testing without actual Redis
mock_redis = True 

broker_url = "memory://" if mock_redis else redis_url
backend_url = "cache+memory://" if mock_redis else redis_url

celery_app = Celery(
    "backend",
    broker=broker_url,
    backend=backend_url,
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
    task_always_eager=mock_redis,
    task_eager_propagates=mock_redis,
)

if __name__ == "__main__":
    celery_app.start()
