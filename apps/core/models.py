from django.db import models
from apps.core.services import ActionMixin


class TimestampedModel(ActionMixin, models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
