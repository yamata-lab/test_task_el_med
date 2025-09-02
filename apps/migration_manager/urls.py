"""
URL configuration for the migration_manager API.
"""
from rest_framework.routers import DefaultRouter
from .views import MigrationTargetViewSet, MigrationViewSet

app_name = "migration_manager"

router = DefaultRouter()
router.register(r"migration-targets", MigrationTargetViewSet, basename="migration-targets")
router.register(r"migrations", MigrationViewSet, basename="migrations")

urlpatterns = router.urls
