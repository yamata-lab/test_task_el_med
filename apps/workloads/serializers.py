"""
Serializers for the workloads application.

This module defines how Workload, Credentials, and MountPoint model instances
are converted to and from JSON representations for use in the REST API.
It also enforces business logic and validation at the API layer.
"""
from rest_framework import serializers
from .models import Credentials, Workload, MountPoint


class CredentialsSerializer(serializers.ModelSerializer):
    """Serializer for the Credentials model."""
    class Meta:
        model = Credentials
        # Exclude password from read responses for security.
        # It's write-only.
        extra_kwargs = {'password': {'write_only': True}}
        fields = ('id', 'username', 'password', 'domain', 'created_at', 'updated_at')


class MountPointSerializer(serializers.ModelSerializer):
    """Serializer for the MountPoint model."""
    class Meta:
        model = MountPoint
        # 'workload' is excluded because it will be managed via the nested
        # relationship in WorkloadSerializer.
        fields = ('id', 'name', 'size_gb')


class WorkloadSerializer(serializers.ModelSerializer):
    """
    Serializer for the Workload model with nested MountPoint management.
    """
    mount_points = MountPointSerializer(many=True)
    # Use PrimaryKeyRelatedField for writable relationship, but include
    # a read-only string representation for better browsable API experience.
    credentials_details = CredentialsSerializer(source='credentials', read_only=True)

    class Meta:
        model = Workload
        fields = (
            'id',
            'name',
            'ip_address',
            'credentials',
            'credentials_details',
            'mount_points',
            'created_at',
            'updated_at',
        )
        # credentials field is for writing (accepts a UUID), while
        # credentials_details is for reading (shows nested object).
        extra_kwargs = {'credentials': {'write_only': True}}


    def create(self, validated_data):
        """
        Handle creation of a Workload and its nested MountPoints.
        """
        mount_points_data = validated_data.pop('mount_points')
        workload = Workload.objects.create(**validated_data)
        for mount_point_data in mount_points_data:
            MountPoint.objects.create(workload=workload, **mount_point_data)
        return workload

    def update(self, instance, validated_data):
        """
        Handle updates for a Workload and its nested MountPoints.

        This method enforces the business rule that `ip_address` cannot be changed.
        """
        # Enforce immutability of ip_address at the API layer.
        validated_data.pop('ip_address', None)
        
        mount_points_data = validated_data.pop('mount_points', None)
        
        # Update the Workload instance fields
        instance = super().update(instance, validated_data)

        # Handle nested MountPoints update if provided
        if mount_points_data is not None:
            # Clear existing mount points and create new ones.
            # A more sophisticated implementation could diff the sets.
            instance.mount_points.all().delete()
            for mount_point_data in mount_points_data:
                MountPoint.objects.create(workload=instance, **mount_point_data)

        return instance
