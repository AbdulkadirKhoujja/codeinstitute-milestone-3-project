from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from news.models import Category
from news.models import Post


class PublishedPostFeedTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        author = get_user_model().objects.create_user(
            username="feed-author",
            password="Existing-passphrase-284!",
        )
        category = Category.objects.create(
            name="Startups",
            slug="startups",
            description="Startup stories.",
        )
        cls.older_post = Post.objects.create(
            title="Older published story",
            summary="An older story summary.",
            article_url="https://example.com/older",
            content="Older story context.",
            author=author,
            category=category,
            status=Post.Status.PUBLISHED,
        )
        cls.newer_post = Post.objects.create(
            title="Newer published story",
            summary="A newer story summary.",
            article_url="https://example.com/newer",
            content="Newer story context.",
            author=author,
            category=category,
            status=Post.Status.PUBLISHED,
        )
        cls.draft_post = Post.objects.create(
            title="Private draft story",
            summary="A private draft summary.",
            article_url="https://example.com/draft",
            content="Draft context.",
            author=author,
            category=category,
            status=Post.Status.DRAFT,
        )
        now = timezone.now()
        Post.objects.filter(pk=cls.older_post.pk).update(
            created_at=now - timedelta(days=1)
        )
        Post.objects.filter(pk=cls.newer_post.pk).update(created_at=now)

    def test_feed_contains_only_published_posts_newest_first(self):
        response = self.client.get(reverse("news:home"))

        self.assertQuerySetEqual(
            response.context["posts"],
            [self.newer_post, self.older_post],
        )
