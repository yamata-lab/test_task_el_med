"""Data models for managing the migration process."""

from django.db import models
from apps.common.models import TimestampedModel
from apps.workloads.models import Credentials, Workload, MountPoint



class MigrationTarget(TimestampedModel):
    """
    Defines the destination for a migration.

    This model specifies where a workload should be migrated to, including the
    cloud platform, necessary credentials, and the target VM configuration.
    """
    class CloudType(models.TextChoices):
        """Enumeration for supported cloud platforms."""
        AWS = "aws", "Amazon Web Services"
        AZURE = "azure", "Microsoft Azure"
        VSPHERE = "vsphere", "VMware vSphere"
        VCLOUD = "vcloud", "VMware vCloud"

    cloud_type = models.CharField(
        max_length=10,
        choices=CloudType.choices,
        help_text="The target cloud platform."
    )
    cloud_credentials = models.ForeignKey(
        Credentials,
        on_delete=models.PROTECT,
        related_name="migration_targets",
        help_text="Credentials for accessing the target cloud environment."
    )
    target_vm = models.OneToOneField(
        Workload,
        on_delete=models.CASCADE,
        related_name="migration_target_vm",
        help_text="The workload object representing the target virtual machine."
    )

    def __str__(self):
        """Return a string representation of the migration target."""
        return f"Target: {self.get_cloud_type_display()} for {self.target_vm.name}"

    class Meta(TimestampedModel.Meta):
        verbose_name = "Migration Target"
        verbose_name_plural = "Migration Targets"


class Migration(TimestampedModel):
    """

    Represents a single migration job, tracking its state and configuration.
    """
    class MigrationState(models.TextChoices):
        """Enumeration for the states of a migration process."""
        NOT_STARTED = "not_started", "Not Started"
        RUNNING = "running", "Running"
        ERROR = "error", "Error"
        SUCCESS = "success", "Success"

    source = models.ForeignKey(
        Workload,
        on_delete=models.CASCADE,
        related_name="source_migrations",
        help_text="The source workload to be migrated."
    )
    target = models.ForeignKey(
        MigrationTarget,
        on_delete=models.CASCADE,
        related_name="target_migrations",
        help_text="The configured destination for the migration."
    )
    state = models.CharField(
        max_length=20,
        choices=MigrationState.choices,
        default=MigrationState.NOT_STARTED,
        db_index=True,
        help_text="The current state of the migration process."
    )
    selected_mount_points = models.ManyToManyField(
        MountPoint,
        related_name="migrations",
        help_text="The specific mount points selected for this migration."
    )
    
    def run(self):
        """Dispatches a Celery task to run the migration.
        The import is done locally within the method to prevent circular
        dependencies at application startup.
        """
        from .tasks import execute_migration_task
        
        execute_migration_task.delay(migration_id=str(self.id))

    def __str__(self):
        """Return a string representation of the migration."""
        return f"Migration of {self.source.name} to {self.target.get_cloud_type_display()} [{self.get_state_display()}]"

    class Meta(TimestampedModel.Meta):
        verbose_name = "Migration"
        verbose_name_plural = "Migrations"
