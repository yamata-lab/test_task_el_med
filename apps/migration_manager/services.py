"""Service layer containing the core business logic for migrations."""
import time
from typing import TYPE_CHECKING
from django.db import transaction
from django.core.exceptions import ValidationError

from apps.workloads.models import MountPoint

import logging

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .models import Migration

SIMULATION_SLEEP_SECONDS = 10
REQUIRED_SYSTEM_MOUNT_POINT = "c:\\"

def run_migration_logic(migration: "Migration"):
    """
    Contains the actual business logic for executing a migration.
    This function is decoupled from Celery and can be tested or reused easily.
    """
    # Pre-flight checks
    if migration.state != migration.MigrationState.NOT_STARTED:
        raise ValidationError("Migration has already been started or completed.")

    selected_mount_point_names = {mp.name.lower().strip() for mp in migration.selected_mount_points.all()}
    if REQUIRED_SYSTEM_MOUNT_POINT not in selected_mount_point_names:
        raise ValidationError("Cannot start migration: The system mount point 'C:\\' is not selected.")

    # Transition to 'RUNNING' state.
    migration.state = migration.MigrationState.RUNNING
    migration.save(update_fields=['state'])

    try:
        logger.info(f"Starting migration simulation for {migration.id}...")
        time.sleep(SIMULATION_SLEEP_SECONDS)
        logger.info("Simulation finished. Copying mount points...")

        with transaction.atomic():
            target_vm = migration.target.target_vm
            target_vm.mount_points.all().delete()
            
            new_mount_points = [
                MountPoint(workload=target_vm, name=mp.name, size_gb=mp.size_gb)
                for mp in migration.selected_mount_points.all()
            ]
            MountPoint.objects.bulk_create(new_mount_points)

        migration.state = migration.MigrationState.SUCCESS
        logger.info(f"Migration {migration.id} completed successfully.")

    except Exception as e:
        migration.state = migration.MigrationState.ERROR
        logger.info(f"An error occurred during migration {migration.id}: {e}")
        raise
    
    finally:
        migration.save(update_fields=['state'])
