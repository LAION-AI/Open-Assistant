from __future__ import absolute_import

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from oasst_backend.scheduled_tasks import app as celery_app

__all__ = ("celery_app",)
