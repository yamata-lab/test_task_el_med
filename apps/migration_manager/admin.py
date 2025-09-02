"""
Django Admin configuration for the 'migration_manager' application.

This configuration customizes the admin interface for migration-related models,
providing better visualization of the migration process, states, and relationships.
"""
from django.contrib import admin
from .models import MigrationTarget, Migration


@admin.register(MigrationTarget)
class MigrationTargetAdmin(admin.ModelAdmin):
    """Admin configuration for the MigrationTarget model."""
    list_display = ('id', 'cloud_type', 'target_vm', 'updated_at')
    list_filter = ('cloud_type',)
    search_fields = ('target_vm__name', 'target_vm__ip_address')
    list_select_related = ('target_vm', 'cloud_credentials')
    readonly_fields = ('created_at', 'updated_at', 'id')


@admin.register(Migration)
class MigrationAdmin(admin.ModelAdmin):
    """Admin configuration for the Migration model."""
    list_display = ('id', 'source', 'target', 'state', 'updated_at')
    list_filter = ('state', 'target__cloud_type')
    search_fields = ('source__name', 'source__ip_address')
    list_select_related = ('source', 'target')
    readonly_fields = ('created_at', 'updated_at', 'id')
    
    # Autocomplete fields are a user-friendly way to select from a large
    # number of related objects.
    autocomplete_fields = ['source', 'target', 'selected_mount_points']
    
    fieldsets = (
        ('Overview', {
            'fields': ('id', 'state')
        }),
        ('Source & Target', {
            'fields': ('source', 'target')
        }),
        ('Configuration', {
            'fields': ('selected_mount_points',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Make this section collapsible
        }),
    )
