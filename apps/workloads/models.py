"""Data models for representing IT workloads and their components."""

from django.db import models
from django.core.exceptions import ValidationError
from encrypted_model_fields.fields import EncryptedCharField
from dirtyfields import DirtyFieldsMixin
from apps.common.models import TimestampedModel


class Credentials(TimestampedModel):
    """
    Represents a set of credentials for accessing a system.

    Attributes:
        username (str): The username for authentication.
        password (str): The password for authentication. This field is
            automatically encrypted before being saved to the database.
        domain (str, optional): The domain associated with the credentials.
    """
    username = models.CharField(
        max_length=255,
        help_text="The username for the credentials."
    )
    password = EncryptedCharField(
        max_length=255,
        help_text="Encrypted password for the credentials."
    )
    domain = models.CharField(
        max_length=255,
        blank=True,
        help_text="The network domain, if applicable (e.g., Active Directory)."
    )

    def __str__(self):
        """Return a string representation of the credentials."""
        return f"{self.domain}\\{self.username}" if self.domain else self.username

    class Meta:
        verbose_name = "Credential Set"
        verbose_name_plural = "Credential Sets"


class Workload(DirtyFieldsMixin, TimestampedModel):
    """
    Represents a source or target server/virtual machine.

    This is a central model representing a computing workload, identified by its
    unique IP address. It includes logic to prevent the IP address from being
    changed after the object has been created.
    """
    name = models.CharField(
        max_length=255,
        help_text="A human-readable name for the workload (e.g., 'Primary DB Server')."
    )
    ip_address = models.GenericIPAddressField(
        unique=True,
        db_index=True,
        help_text="The unique IP address of the workload. Cannot be changed after creation."
    )
    credentials = models.ForeignKey(
        Credentials,
        on_delete=models.PROTECT,
        related_name="workloads",
        help_text="Credentials required to access this workload."
    )
    
    def save(self, *args, **kwargs):
        is_new = self._state.adding or self.pk is None
        
        if not is_new and 'ip_address' in self.get_dirty_fields():
            raise ValidationError("The IP address of a workload cannot be changed.")

        super().save(*args, **kwargs)

    def __str__(self):
        """Return a string representation of the workload."""
        return f"{self.name} ({self.ip_address})"

    class Meta(TimestampedModel.Meta):
        verbose_name = "Workload"
        verbose_name_plural = "Workloads"


class MountPoint(TimestampedModel):
    """
    Represents a storage volume or mount point associated with a Workload.

    Attributes:
        workload (Workload): The workload to which this mount point belongs.
        name (str): The name of the mount point (e.g., 'C:\\', '/mnt/data').
        size_gb (int): The total size of the volume in gigabytes.
    """
    workload = models.ForeignKey(
        Workload,
        on_delete=models.CASCADE,
        related_name="mount_points",
        help_text="The workload this mount point is attached to."
    )
    name = models.CharField(
        max_length=255,
        help_text="The name or path of the mount point (e.g., 'C:\\' or '/var/log')."
    )
    size_gb = models.PositiveIntegerField(
        help_text="The total size of the volume in gigabytes (GB)."
    )

    def __str__(self):
        """Return a string representation of the mount point."""
        return f"{self.workload.name}: {self.name} ({self.size_gb} GB)"

    class Meta(TimestampedModel.Meta):
        # A mount point name should be unique for a given workload.
        unique_together = ('workload', 'name')
        verbose_name = "Mount Point"
        verbose_name_plural = "Mount Points"
