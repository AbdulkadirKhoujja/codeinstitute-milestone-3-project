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

    def test_feed_renders_accessible_story_cards_with_metadata(self):
        response = self.client.get(reverse("news:home"))

        self.assertTemplateUsed(response, "includes/post-card.html")
        self.assertContains(response, self.newer_post.title)
        self.assertContains(response, self.newer_post.summary)
        self.assertContains(response, self.newer_post.category.name)
        self.assertContains(response, self.newer_post.author.username)
        self.assertContains(
            response,
            f'href="{reverse("news:post-detail", args=[self.newer_post.pk])}"',
        )
        self.assertContains(
            response,
            f'href="{reverse("accounts:profile", args=[self.newer_post.author.username])}"',
        )
        self.assertContains(response, '<time datetime="')
        content = response.content.decode()
        self.assertLess(
            content.index(self.newer_post.title),
            content.index(self.older_post.title),
        )


class CategoryFilterTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        author = get_user_model().objects.create_user(
            username="category-author",
            password="Existing-passphrase-284!",
        )
        cls.ai_category = Category.objects.create(
            name="Artificial Intelligence",
            slug="artificial-intelligence",
            description="Artificial intelligence stories.",
        )
        cls.startup_category = Category.objects.create(
            name="Startups",
            slug="startups",
            description="Startup stories.",
        )
        cls.ai_post = Post.objects.create(
            title="AI category story",
            summary="An AI story summary.",
            article_url="https://example.com/ai-category",
            content="AI category context.",
            author=author,
            category=cls.ai_category,
            status=Post.Status.PUBLISHED,
        )
        cls.startup_post = Post.objects.create(
            title="Startup category story",
            summary="A startup story summary.",
            article_url="https://example.com/startup-category",
            content="Startup category context.",
            author=author,
            category=cls.startup_category,
            status=Post.Status.PUBLISHED,
        )

    def test_category_query_narrows_feed_and_identifies_active_filter(self):
        response = self.client.get(
            reverse("news:home"),
            {"category": self.startup_category.slug},
        )

        self.assertQuerySetEqual(response.context["posts"], [self.startup_post])
        self.assertEqual(response.context["active_category"], self.startup_category)
        self.assertContains(response, "Startups stories")
        self.assertContains(response, self.startup_post.title)
        self.assertNotContains(response, self.ai_post.title)
        self.assertContains(response, f'href="{reverse("news:home")}"')

    def test_feed_exposes_categories_in_alphabetical_order(self):
        response = self.client.get(reverse("news:home"))

        self.assertQuerySetEqual(
            response.context["categories"],
            [self.ai_category, self.startup_category],
        )
