"""Tests for the models in the workloads application."""

from django.test import TestCase
from django.core.exceptions import ValidationError
from apps.workloads.models import Credentials, Workload


class WorkloadModelTests(TestCase):
    """Test suite for the Workload model."""

    @classmethod
    def setUpTestData(cls):
        """Set up non-modified objects used by all test methods."""
        cls.credentials = Credentials.objects.create(username="test", password="password")

    def test_workload_creation(self):
        """Test that a Workload can be created successfully."""
        workload = Workload.objects.create(
            name="Test Server",
            ip_address="192.168.1.1",
            credentials=self.credentials,
        )
        self.assertEqual(str(workload), "Test Server (192.168.1.1)")
        self.assertEqual(Workload.objects.count(), 1)

    def test_ip_address_immutability(self):
        """
        Test that changing the IP address of an existing Workload raises a
        ValidationError.
        """
        workload = Workload.objects.create(
            name="Immutable Server",
            ip_address="192.168.1.2",
            credentials=self.credentials,
        )
        
        # Assert that attempting to change the IP and save raises an error.
        with self.assertRaises(ValidationError) as context:
            workload.ip_address = "192.168.1.3"
            workload.save()
            
        self.assertIn("The IP address of a workload cannot be changed", str(context.exception))
        
        # Verify that the IP address was not actually changed in the database.
        workload.refresh_from_db()
        self.assertEqual(workload.ip_address, "192.168.1.2")
