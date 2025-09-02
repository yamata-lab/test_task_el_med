"""
Serializers for the migration_manager application.
"""
from rest_framework import serializers
from apps.workloads.serializers import WorkloadSerializer
from .models import MigrationTarget, Migration


class MigrationTargetSerializer(serializers.ModelSerializer):
    """Serializer for the MigrationTarget model."""
    target_vm_details = WorkloadSerializer(source='target_vm', read_only=True)

    class Meta:
        model = MigrationTarget
        fields = (
            'id',
            'cloud_type',
            'cloud_credentials',
            'target_vm',
            'target_vm_details',
            'created_at',
            'updated_at',
        )
        extra_kwargs = {
            'target_vm': {'write_only': True},
            'cloud_credentials': {'write_only': True},
        }


class MigrationSerializer(serializers.ModelSerializer):
    """Serializer for the Migration model."""
    # Read-only nested serializers for detailed GET responses
    source_details = WorkloadSerializer(source='source', read_only=True)
    target_details = MigrationTargetSerializer(source='target', read_only=True)

    class Meta:
        model = Migration
        fields = (
            'id',
            'source',
            'target',
            'state',
            'selected_mount_points',
            'source_details',
            'target_details',
            'created_at',
            'updated_at',
        )
        # The 'state' field should be managed by the system, not by the client.
        read_only_fields = ('state',)
