from celery import Celery
from app.config import settings

# Crear instancia de Celery
celery_app = Celery(
    "documentacion_rag",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks.processing_tasks"]
)

# Configuración de Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutos
    task_soft_time_limit=25 * 60,  # 25 minutos
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
) 