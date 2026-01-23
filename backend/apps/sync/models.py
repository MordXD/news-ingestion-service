"""
Модель SyncLog — логирование выполнения пайплайна ingestion.

Используется для:
- диагностики асинхронных задач
- контроля стабильности обработки
- аудита операций
"""
from django.db import models

from apps.feeds.models import Feed


class SyncLog(models.Model):
    """Лог синхронизации фида - операционная видимость"""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SUCCESS = 'success', 'Success'
        FAILED = 'failed', 'Failed'

    feed = models.ForeignKey(
        Feed,
        on_delete=models.CASCADE,
        related_name='sync_logs'
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    items_found = models.PositiveIntegerField(default=0)
    items_created = models.PositiveIntegerField(default=0)
    items_updated = models.PositiveIntegerField(default=0)

    error_message = models.TextField(blank=True)

    task_id = models.CharField(max_length=255, blank=True, db_index=True)

    class Meta:
        ordering = ['-started_at']
        db_table = 'sync_logs'
        indexes = [
            models.Index(fields=['feed', '-started_at']),
            models.Index(fields=['status', '-started_at']),
        ]

    def __str__(self) -> str:
        return f"{self.feed.url} - {self.status} - {self.started_at}"

    @property
    def duration_seconds(self) -> float | None:
        """Длительность синхронизации в секундах"""
        if self.finished_at and self.started_at:
            return (self.finished_at - self.started_at).total_seconds()
        return None