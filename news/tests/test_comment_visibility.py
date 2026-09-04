from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from news.models import Category
from news.models import Comment
from news.models import Post


class ApprovedCommentVisibilityTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = get_user_model().objects.create_user(
            username="discussion-author",
            password="Existing-passphrase-284!",
        )
        category = Category.objects.create(
            name="Community",
            slug="community",
            description="Community stories.",
        )
        cls.post = Post.objects.create(
            title="A story with discussion",
            summary="Discussion summary.",
            article_url="https://example.com/discussion",
            content="Discussion context.",
            author=cls.author,
            category=category,
            status=Post.Status.PUBLISHED,
        )
        cls.approved = Comment.objects.create(
            post=cls.post,
            author=cls.author,
            body="An approved contribution.",
            is_approved=True,
        )
        cls.unapproved = Comment.objects.create(
            post=cls.post,
            author=cls.author,
            body="A contribution awaiting review.",
            is_approved=False,
        )

    def test_public_detail_displays_only_approved_comments(self):
        response = self.client.get(
            reverse("news:post-detail", args=[self.post.pk])
        )

        self.assertQuerySetEqual(response.context["comments"], [self.approved])
        self.assertContains(response, self.approved.body)
        self.assertContains(response, self.author.username)
        self.assertContains(response, 'datetime="')
        self.assertNotContains(response, self.unapproved.body)

    def test_author_sees_own_unapproved_comment_with_clear_label(self):
        self.client.force_login(self.author)

        response = self.client.get(
            reverse("news:post-detail", args=[self.post.pk])
        )

        self.assertQuerySetEqual(
            response.context["comments"],
            [self.approved, self.unapproved],
        )
        self.assertContains(response, self.unapproved.body)
        self.assertContains(response, "Awaiting moderation")

    def test_comment_management_links_are_visible_only_to_owner(self):
        update_url = reverse(
            "news:comment-update",
            args=[self.post.pk, self.approved.pk],
        )
        delete_url = reverse(
            "news:comment-delete",
            args=[self.post.pk, self.approved.pk],
        )
        visitor_response = self.client.get(
            reverse("news:post-detail", args=[self.post.pk])
        )
        self.assertNotContains(visitor_response, update_url)
        self.assertNotContains(visitor_response, delete_url)

        self.client.force_login(self.author)
        owner_response = self.client.get(
            reverse("news:post-detail", args=[self.post.pk])
        )
        self.assertContains(owner_response, update_url)
        self.assertContains(owner_response, delete_url)
