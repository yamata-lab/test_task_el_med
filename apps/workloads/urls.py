"""
URL configuration for the workloads API.

This module uses a DRF DefaultRouter to automatically generate the URLs
for the Credentials and Workload ViewSets.
"""
from rest_framework.routers import DefaultRouter
from .views import CredentialsViewSet, WorkloadViewSet

app_name = "workloads"

router = DefaultRouter()
router.register(r"credentials", CredentialsViewSet, basename="credentials")
router.register(r"workloads", WorkloadViewSet, basename="workloads")

urlpatterns = router.urls
