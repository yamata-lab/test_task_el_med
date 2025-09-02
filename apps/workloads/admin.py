"""
Django Admin configuration for the 'workloads' application.

This file defines how the models from the 'workloads' app are displayed and
managed in the Django admin interface. Customizations are made to improve
usability for administrators, such as adding search, filtering, and inline
editing capabilities.
"""
from django.contrib import admin
from .models import Credentials, Workload, MountPoint


class MountPointInline(admin.TabularInline):
    """
    Allows editing MountPoint objects directly on the Workload admin page.

    Using a TabularInline provides a compact, table-based interface for managing
    related MountPoint instances, which is ideal for this one-to-many relationship.
    """
    model = MountPoint
    extra = 1  # Show one extra blank form for adding a new mount point.
    fields = ('name', 'size_gb')


@admin.register(Credentials)
class CredentialsAdmin(admin.ModelAdmin):
    """Admin configuration for the Credentials model."""
    list_display = ('id', 'username', 'domain', 'updated_at')
    search_fields = ('username', 'domain')
    readonly_fields = ('created_at', 'updated_at', 'id')


@admin.register(Workload)
class WorkloadAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Workload model.

    Includes an inline for managing associated MountPoints directly.
    """
    list_display = ('name', 'ip_address', 'credentials', 'updated_at')
    search_fields = ('name', 'ip_address')
    list_select_related = ('credentials',)  # Optimize query performance
    readonly_fields = ('created_at', 'updated_at', 'id')
    inlines = [MountPointInline]


@admin.register(MountPoint)
class MountPointAdmin(admin.ModelAdmin):
    """Admin configuration for the MountPoint model."""
    list_display = ('name', 'workload', 'size_gb', 'updated_at')
    search_fields = ('name', 'workload__name', 'workload__ip_address')
    list_select_related = ('workload',)
    readonly_fields = ('created_at', 'updated_at', 'id')
