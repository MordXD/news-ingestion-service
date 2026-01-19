from django.db import models

from apps.feeds.models import Feed


class Article(models.Model):
    """Статья из RSS/Atom ленты с идемпотентностью через уникальную пару (feed, external_id)"""

    id = models.BigAutoField(primary_key=True)
    external_id = models.CharField(
        max_length=500,
        help_text='guid from RSS or id from Atom'
    )
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE, related_name='articles')

    title = models.CharField(max_length=1000)
    link = models.URLField()
    summary = models.TextField(blank=True)
    content = models.TextField(blank=True)

    published_at = models.DateTimeField(null=True, blank=True)
    fetched_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at', '-fetched_at']
        db_table = 'articles'
        constraints = [
            models.UniqueConstraint(
                fields=['feed', 'external_id'],
                name='unique_article_per_feed'
            ),
            models.UniqueConstraint(
                fields=['feed', 'link'],
                name='unique_article_link_per_feed',
                condition=models.Q(external_id='')
            ),
        ]
        indexes = [
            models.Index(fields=['feed', '-published_at']),
            models.Index(fields=['feed', 'external_id']),
            models.Index(fields=['-fetched_at']),
        ]

    def __str__(self) -> str:
        return self.title[:100]