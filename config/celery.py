"""
Celery application instance definition.

This module defines the Celery application instance that is used by the Celery
worker and any other process that needs to interact with Celery (e.g., to
dispatch tasks from a Django view).
"""

import os
from celery import Celery

# This line ensures that the Django settings are available to the Celery worker.
# It's a crucial link between the Celery process and the Django project.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('migration_project')

# This method configures Celery using the Django settings file.
# The `namespace='CELERY'` argument means all Celery-related configuration
# settings in `settings.py` must be prefixed with 'CELERY_', e.g., CELERY_BROKER_URL.
app.config_from_object('django.conf:settings', namespace='CELERY')

# This method automatically discovers and loads tasks from a `tasks.py` file
# in each of the applications listed in `INSTALLED_APPS`.
app.autodiscover_tasks()
