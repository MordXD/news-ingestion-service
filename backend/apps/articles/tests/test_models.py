import pytest
from django.db import IntegrityError
from apps.feeds.models import Feed
from apps.articles.models import Article


@pytest.mark.django_db
class TestArticleModel:
    """Тесты модели Article."""

    @pytest.fixture
    def feed(self):
        return Feed.objects.create(url='https://example.com/rss.xml')

    def test_create_article(self, feed):
        """Article создаётся с корректными полями."""
        article = Article.objects.create(
            feed=feed,
            external_id='guid-123',
            title='Test Article',
            link='https://example.com/article',
            summary='Summary text',
            content='Full content'
        )

        assert article.id is not None
        assert article.external_id == 'guid-123'
        assert article.title == 'Test Article'
        assert article.feed == feed

    def test_article_str(self, feed):
        """__str__ возвращает обрезанный title."""
        article = Article.objects.create(
            feed=feed,
            external_id='guid-123',
            title='A' * 150,
            link='https://example.com/article'
        )
        assert str(article) == 'A' * 100

    def test_unique_constraint(self, feed):
        """Нельзя создать дубликат (feed, external_id)."""
        Article.objects.create(
            feed=feed,
            external_id='same-id',
            title='Article 1',
            link='https://example.com/1'
        )

        with pytest.raises(IntegrityError):
            Article.objects.create(
                feed=feed,
                external_id='same-id',
                title='Article 2',
                link='https://example.com/2'
            )

    def test_different_feeds_same_external_id(self, feed):
        """Один external_id может быть в разных фидах."""
        feed2 = Feed.objects.create(url='https://other.com/rss.xml')

        Article.objects.create(
            feed=feed,
            external_id='same-id',
            title='Article 1',
            link='https://example.com/1'
        )

        # Это должно работать - разные фиды
        article2 = Article.objects.create(
            feed=feed2,
            external_id='same-id',
            title='Article 2',
            link='https://other.com/1'
        )

        assert article2.id is not None
