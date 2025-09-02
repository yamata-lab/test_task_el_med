"""Celery tasks for the migration_manager application."""
from uuid import UUID
from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
from .models import Migration
from .services import run_migration_logic
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def execute_migration_task(self, migration_id: str):
    """
    A lean Celery task that fetches a migration object and delegates the
    business logic to the service layer.
    """
    try:
        migration = Migration.objects.get(id=UUID(migration_id))
        logger.info(f"Celery task picked up migration: {migration.id}")
        # Delegate the actual work to the service layer
        run_migration_logic(migration=migration)
        return f"Migration {migration.id} processed."
    except ObjectDoesNotExist:
        logger.error(f"Error: Migration with ID {migration_id} not found. Task will not be retried.")
        return f"Migration {migration_id} not found."
    except Exception as exc:
        # If the service layer raised an error, Celery's retry mechanism will catch it.
        logger.error(f"Task for migration {migration_id} failed: {exc}. Retrying...")
        self.retry(exc=exc)
