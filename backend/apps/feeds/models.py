from django.db import models
from django.core.validators import URLValidator


class Feed(models.Model):
    """RSS/Atom статьи"""

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        ERROR = 'error', 'Error'
        DISABLED = 'disabled', 'Disabled'

    url = models.URLField(validators=[URLValidator()], unique=True)
    title = models.CharField(max_length=500, blank=True)
    description = models.TextField(blank=True)
    link = models.URLField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE
    )
    last_error = models.TextField(blank=True)
    last_fetched_at = models.DateTimeField(null=True, blank=True)
    fetch_interval_minutes = models.PositiveIntegerField(default=60)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        db_table = 'feeds'

    def __str__(self) -> str:
        return self.title or self.url