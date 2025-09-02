"""
Views for the workloads REST API.

This module defines the ViewSets that handle the HTTP requests for
Workload and Credentials resources, linking them to the appropriate
serializers and models.
"""
from rest_framework import viewsets, permissions
from .models import Credentials, Workload
from .serializers import CredentialsSerializer, WorkloadSerializer


class CredentialsViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows credentials to be viewed or edited.
    """
    queryset = Credentials.objects.all()
    serializer_class = CredentialsSerializer
    # In a real app, you would have more restrictive permissions.
    # permission_classes = [permissions.IsAdminUser]


class WorkloadViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows workloads to be viewed or edited.
    
    Provides full CRUD functionality for Workloads and supports nested
    creation and updates of their associated MountPoints.
    """
    serializer_class = WorkloadSerializer
    # queryset is optimized to prevent N+1 query problems by pre-fetching
    # related objects that will be used by the serializer.
    queryset = Workload.objects.all().select_related(
        'credentials'
    ).prefetch_related('mount_points')
    # permission_classes = [permissions.IsAdminUser]
