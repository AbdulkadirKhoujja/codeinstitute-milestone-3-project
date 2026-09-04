from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from news.models import Category
from news.models import Post


class PublicProfileTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.member = get_user_model().objects.create_user(
            username="profile-member",
            email="private@example.com",
            password="Existing-passphrase-284!",
        )
        cls.category = Category.objects.create(
            name="Software",
            slug="software",
            description="Software stories.",
        )
        cls.published_post = Post.objects.create(
            title="A published profile story",
            summary="A useful published summary.",
            article_url="https://example.com/published",
            content="Published context.",
            author=cls.member,
            category=cls.category,
            status=Post.Status.PUBLISHED,
        )
        cls.draft_post = Post.objects.create(
            title="A private draft story",
            summary="A draft summary.",
            article_url="https://example.com/draft",
            content="Draft context.",
            author=cls.member,
            category=cls.category,
            status=Post.Status.DRAFT,
        )

    def test_profile_shows_public_member_information_and_published_posts(self):
        response = self.client.get(
            reverse("accounts:profile", args=[self.member.username])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/profile.html")
        self.assertContains(response, "profile-member")
        self.assertContains(response, "Member since")
        self.assertContains(response, self.published_post.title)
        self.assertContains(
            response,
            f'href="{reverse("news:post-detail", args=[self.published_post.pk])}"',
        )
        self.assertNotContains(response, self.draft_post.title)
        self.assertNotContains(response, self.member.email)

    def test_unknown_member_returns_not_found(self):
        response = self.client.get(
            reverse("accounts:profile", args=["missing-member"])
        )

        self.assertEqual(response.status_code, 404)


class ProfileDraftPrivacyTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.member = get_user_model().objects.create_user(
            username="draft-owner",
            password="Existing-passphrase-284!",
        )
        cls.other_member = get_user_model().objects.create_user(
            username="another-member",
            password="Existing-passphrase-284!",
        )
        category = Category.objects.create(
            name="Security",
            slug="security",
            description="Security stories.",
        )
        cls.draft_post = Post.objects.create(
            title="An owner-only draft",
            summary="Private work in progress.",
            article_url="https://example.com/private-draft",
            content="Draft context.",
            author=cls.member,
            category=category,
            status=Post.Status.DRAFT,
        )

    def test_profile_owner_sees_draft_with_status(self):
        self.client.force_login(self.member)

        response = self.client.get(
            reverse("accounts:profile", args=[self.member.username])
        )

        self.assertContains(response, "Your stories")
        self.assertContains(response, self.draft_post.title)
        self.assertContains(response, "Draft")
        self.assertContains(
            response,
            f'href="{reverse("news:post-create")}"',
        )
        self.assertContains(
            response,
            f'href="{reverse("news:post-update", args=[self.draft_post.pk])}"',
        )
        self.assertContains(
            response,
            f'href="{reverse("news:post-delete", args=[self.draft_post.pk])}"',
        )

    def test_other_member_cannot_see_profile_draft(self):
        self.client.force_login(self.other_member)

        response = self.client.get(
            reverse("accounts:profile", args=[self.member.username])
        )

        self.assertNotContains(response, self.draft_post.title)
