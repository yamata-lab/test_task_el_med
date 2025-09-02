"""Tests for the models in the migration_manager application."""

from django.test import TestCase
from apps.workloads.models import Credentials, Workload, MountPoint
from apps.migration_manager.models import MigrationTarget, Migration


class MigrationModelsTests(TestCase):
    """Test suite for Migration and MigrationTarget models."""

    @classmethod
    def setUpTestData(cls):
        """
        Set up a common set of objects for all tests in this class.
        This runs only once, making tests faster.
        """
        # Credentials
        cls.source_creds = Credentials.objects.create(username="source", password="p")
        cls.target_creds = Credentials.objects.create(username="target", password="p")

        # Workloads
        cls.source_workload = Workload.objects.create(
            name="Source Server", ip_address="192.168.1.10", credentials=cls.source_creds
        )
        cls.target_workload = Workload.objects.create(
            name="Target VM", ip_address="10.0.0.5", credentials=cls.target_creds
        )

        # Mount Points for the source
        cls.mp_c = MountPoint.objects.create(workload=cls.source_workload, name="C:\\", size_gb=100)

    def test_migration_target_creation(self):
        """Test that a MigrationTarget can be created successfully."""
        target = MigrationTarget.objects.create(
            cloud_type=MigrationTarget.CloudType.AWS,
            cloud_credentials=self.target_creds,
            target_vm=self.target_workload,
        )
        self.assertEqual(MigrationTarget.objects.count(), 1)
        expected_str = f"Target: Amazon Web Services for Target VM"
        self.assertEqual(str(target), expected_str)

    def test_migration_creation(self):
        """Test that a Migration can be created successfully."""
        target = MigrationTarget.objects.create(
            cloud_type=MigrationTarget.CloudType.AWS,
            cloud_credentials=self.target_creds,
            target_vm=self.target_workload,
        )
        migration = Migration.objects.create(
            source=self.source_workload,
            target=target,
        )
        migration.selected_mount_points.set([self.mp_c])

        self.assertEqual(Migration.objects.count(), 1)
        # Check default state
        self.assertEqual(migration.state, Migration.MigrationState.NOT_STARTED)
        # Check M2M relationship
        self.assertEqual(migration.selected_mount_points.count(), 1)
        self.assertEqual(migration.selected_mount_points.first(), self.mp_c)

        # Check __str__ representation
        expected_str = f"Migration of Source Server to Amazon Web Services [Not Started]"
        self.assertEqual(str(migration), expected_str)
