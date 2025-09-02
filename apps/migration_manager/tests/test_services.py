"""Tests for the service layer of the migration_manager application."""
from unittest.mock import patch
from django.test import TestCase
from django.core.exceptions import ValidationError

from apps.workloads.models import Credentials, Workload, MountPoint
from apps.migration_manager.models import MigrationTarget, Migration
from apps.migration_manager.services import run_migration_logic


class MigrationServiceTests(TestCase):
    """Test suite for the migration service logic."""

    def setUp(self):
        """Set up a common set of objects for migration tests."""
        # Credentials
        self.source_creds = Credentials.objects.create(username="source", password="p")
        self.target_creds = Credentials.objects.create(username="target", password="p")

        # Workloads
        self.source_workload = Workload.objects.create(
            name="Source Server", ip_address="192.168.1.10", credentials=self.source_creds
        )
        self.target_workload = Workload.objects.create(
            name="Target VM", ip_address="10.0.0.5", credentials=self.target_creds
        )

        # Mount Points for the source
        self.mp_c = MountPoint.objects.create(workload=self.source_workload, name="C:\\", size_gb=100)
        self.mp_d = MountPoint.objects.create(workload=self.source_workload, name="D:\\", size_gb=500)

        # Migration Target
        self.migration_target = MigrationTarget.objects.create(
            cloud_type=MigrationTarget.CloudType.AWS,
            cloud_credentials=self.target_creds,
            target_vm=self.target_workload,
        )

    # Patch 'time.sleep' to make the test run instantly instead of waiting.
    @patch("time.sleep", return_value=None)
    def test_run_migration_success_scenario(self, mock_sleep):
        """
        Test the successful execution of the migration logic.
        """
        # Create a migration instance for the test
        migration = Migration.objects.create(
            source=self.source_workload,
            target=self.migration_target,
        )
        migration.selected_mount_points.set([self.mp_c, self.mp_d])

        # Execute the service function
        run_migration_logic(migration)

        # Assertions
        migration.refresh_from_db()
        self.assertEqual(migration.state, Migration.MigrationState.SUCCESS)

        self.target_workload.refresh_from_db()
        target_mps = self.target_workload.mount_points.all()
        self.assertEqual(target_mps.count(), 2)

        target_mp_names = {mp.name for mp in target_mps}
        self.assertEqual(target_mp_names, {"C:\\", "D:\\"})
        
        # Check that the mock was called, confirming simulation happened
        mock_sleep.assert_called_once()

    def test_run_migration_fails_without_c_drive(self):
        """
        Test that migration fails with a ValidationError if the C: drive is not
        selected.
        """
        migration = Migration.objects.create(
            source=self.source_workload,
            target=self.migration_target,
        )
        # Select only the D: drive
        migration.selected_mount_points.set([self.mp_d])

        with self.assertRaises(ValidationError) as context:
            run_migration_logic(migration)

        expected_message = "Cannot start migration: The system mount point 'C:\\' is not selected."
        self.assertIn(expected_message, context.exception.messages)

        # Verify the migration state is unchanged (or correctly set to error if implemented)
        migration.refresh_from_db()
        self.assertEqual(migration.state, Migration.MigrationState.NOT_STARTED)
