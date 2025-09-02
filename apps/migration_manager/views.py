"""
Views for the migration_manager REST API.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import MigrationTarget, Migration
from .serializers import MigrationTargetSerializer, MigrationSerializer


class MigrationTargetViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Migration Targets to be viewed or edited.
    """
    queryset = MigrationTarget.objects.all().select_related(
        'cloud_credentials', 'target_vm'
    )
    serializer_class = MigrationTargetSerializer


class MigrationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Migrations to be viewed, edited, and run.
    """
    queryset = Migration.objects.all().select_related(
        'source', 'target'
    ).prefetch_related('selected_mount_points')
    serializer_class = MigrationSerializer

    @action(detail=True, methods=['post'], url_path='run')
    def run_migration(self, request, pk=None):
        """
        Custom action to start a migration.

        This endpoint triggers the asynchronous migration process.
        """
        migration = self.get_object()
        
        try:
            # The .run() method dispatches the Celery task
            migration.run()
        except Exception as e:
            # Handle potential validation errors from the service layer, etc.
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Return the serialized migration data with a 202 Accepted status
        serializer = self.get_serializer(migration)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
