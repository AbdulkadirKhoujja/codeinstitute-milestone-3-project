from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from news.models import Category
from news.models import Post


class PublishedPostDetailTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = get_user_model().objects.create_user(
            username="detail-author",
            password="Existing-passphrase-284!",
        )
        cls.category = Category.objects.create(
            name="Artificial Intelligence",
            slug="artificial-intelligence",
            description="Artificial intelligence stories.",
        )
        cls.post = Post.objects.create(
            title="A detailed published story",
            summary="A concise detail-page summary.",
            article_url="https://example.com/original-story",
            content="First context paragraph.\n\nSecond context paragraph.",
            author=cls.author,
            category=cls.category,
            status=Post.Status.PUBLISHED,
        )

    def test_detail_shows_complete_published_story(self):
        response = self.client.get(reverse("news:post-detail", args=[self.post.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "news/post-detail.html")
        self.assertContains(response, self.post.title)
        self.assertContains(response, self.post.summary)
        self.assertContains(response, "First context paragraph.")
        self.assertContains(response, "Second context paragraph.")
        self.assertContains(response, self.author.username)
        self.assertContains(response, self.category.name)
        self.assertContains(response, self.post.article_url)
        self.assertContains(response, 'rel="noopener noreferrer"')
        self.assertContains(response, '<time datetime="')

    def test_unknown_post_returns_not_found(self):
        response = self.client.get(reverse("news:post-detail", args=[999999]))

        self.assertEqual(response.status_code, 404)


class DraftPostDetailPrivacyTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = get_user_model().objects.create_user(
            username="draft-detail-author",
            password="Existing-passphrase-284!",
        )
        cls.other_member = get_user_model().objects.create_user(
            username="draft-detail-visitor",
            password="Existing-passphrase-284!",
        )
        category = Category.objects.create(
            name="Fintech",
            slug="fintech",
            description="Financial technology stories.",
        )
        cls.draft_post = Post.objects.create(
            title="A private detail draft",
            summary="A draft detail summary.",
            article_url="https://example.com/draft-detail",
            content="Private draft context.",
            author=cls.author,
            category=category,
            status=Post.Status.DRAFT,
        )

    def test_anonymous_visitor_receives_not_found_for_draft(self):
        response = self.client.get(
            reverse("news:post-detail", args=[self.draft_post.pk])
        )

        self.assertEqual(response.status_code, 404)

    def test_other_member_receives_not_found_for_draft(self):
        self.client.force_login(self.other_member)

        response = self.client.get(
            reverse("news:post-detail", args=[self.draft_post.pk])
        )

        self.assertEqual(response.status_code, 404)

    def test_owner_can_preview_draft_with_status(self):
        self.client.force_login(self.author)

        response = self.client.get(
            reverse("news:post-detail", args=[self.draft_post.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.draft_post.title)
        self.assertContains(response, "Draft")
