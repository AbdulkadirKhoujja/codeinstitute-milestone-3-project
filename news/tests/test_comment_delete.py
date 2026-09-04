from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from news.models import Category
from news.models import Comment
from news.models import Post


class CommentDeletePageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = get_user_model().objects.create_user(
            username="comment-deleter",
            password="Existing-passphrase-284!",
        )
        category = Category.objects.create(
            name="Comment deletion",
            slug="comment-deletion",
            description="Comment deletion stories.",
        )
        cls.post = Post.objects.create(
            title="Story with removable comment",
            summary="Removable comment summary.",
            article_url="https://example.com/removable-comment",
            content="Removable comment context.",
            author=cls.owner,
            category=category,
            status=Post.Status.PUBLISHED,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.owner,
            body="Comment awaiting deletion.",
            is_approved=True,
        )

    def test_owner_receives_explicit_confirmation_with_cancel_route(self):
        self.client.force_login(self.owner)

        response = self.client.get(
            reverse(
                "news:comment-delete",
                args=[self.post.pk, self.comment.pk],
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "news/comment-confirm-delete.html")
        self.assertContains(response, self.comment.body)
        self.assertContains(response, "cannot be undone")
        self.assertContains(response, 'method="post"')
        self.assertContains(response, 'name="csrfmiddlewaretoken"')
        detail_url = reverse("news:post-detail", args=[self.post.pk])
        self.assertContains(
            response,
            f"{detail_url}#comment-{self.comment.pk}",
        )

    def test_owner_post_deletes_comment_and_returns_to_discussion(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse(
                "news:comment-delete",
                args=[self.post.pk, self.comment.pk],
            ),
            follow=True,
        )

        self.assertFalse(Comment.objects.filter(pk=self.comment.pk).exists())
        detail_url = reverse("news:post-detail", args=[self.post.pk])
        self.assertRedirects(
            response,
            f"{detail_url}#comments-heading",
        )
        self.assertNotContains(response, self.comment.body)
        self.assertContains(response, "Your comment was deleted.")
