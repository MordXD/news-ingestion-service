import pytest
from apps.feeds.models import Feed


@pytest.mark.django_db
class TestFeedModel:
    """Тесты модели Feed."""

    def test_create_feed(self):
        """Feed создаётся с корректными дефолтами."""
        feed = Feed.objects.create(
            url='https://example.com/rss.xml',
            fetch_interval_minutes=60
        )

        assert feed.id is not None
        assert feed.url == 'https://example.com/rss.xml'
        assert feed.status == Feed.Status.ACTIVE
        assert feed.fetch_interval_minutes == 60
        assert feed.title == ''

    def test_feed_str(self):
        """__str__ возвращает title или url."""
        feed = Feed.objects.create(url='https://example.com/rss.xml')
        assert str(feed) == 'https://example.com/rss.xml'

        feed.title = 'Test Feed'
        feed.save()
        assert str(feed) == 'Test Feed'

    def test_feed_status_choices(self):
        """Feed поддерживает статусы active/error/disabled."""
        feed = Feed.objects.create(url='https://example.com/rss.xml')

        feed.status = Feed.Status.ERROR
        feed.save()

        assert feed.status == 'error'

    def test_unique_url(self):
        """URL фида должен быть уникальным."""
        Feed.objects.create(url='https://example.com/rss.xml')

        with pytest.raises(Exception):
            Feed.objects.create(url='https://example.com/rss.xml')
