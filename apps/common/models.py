"""Common models and utilities for the project.

This module contains abstract models and utilities that are shared across
different applications within the project to enforce consistency and reduce
code duplication, following the DRY (Don't Repeat Yourself) principle.
"""
import uuid
from django.db import models


class TimestampedModel(models.Model):
    """An abstract base model providing self-updating timestamp fields.

    This model should be inherited by other models that require auditing
    timestamps. Using `class Meta: abstract = True` ensures that the fields
    from this model are added directly to the child model's database table
    without creating a separate table for `TimestampedModel`.

    Attributes:
        id (UUIDField): The primary key, a universally unique identifier.
        created_at (DateTimeField): The timestamp of object creation.
        updated_at (DateTimeField): The timestamp of the last object update.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="The timestamp when the object was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="The timestamp when the object was last updated."
    )

    class Meta:
        # This ensures the model is not created in the database.
        abstract = True
        # Default ordering for queries, newest first.
        ordering = ['-created_at']
