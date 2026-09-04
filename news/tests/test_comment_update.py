from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from news.models import Category
from news.models import Comment
from news.models import Post


class CommentUpdatePageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = get_user_model().objects.create_user(
            username="comment-owner",
            password="Existing-passphrase-284!",
        )
        category = Category.objects.create(
            name="Comment editing",
            slug="comment-editing",
            description="Comment editing stories.",
        )
        cls.post = Post.objects.create(
            title="Story with editable comment",
            summary="Editable comment summary.",
            article_url="https://example.com/editable-comment",
            content="Editable comment context.",
            author=cls.owner,
            category=category,
            status=Post.Status.PUBLISHED,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.owner,
            body="Comment before editing.",
            is_approved=True,
        )

    def test_owner_receives_prepopulated_comment_form(self):
        self.client.force_login(self.owner)

        response = self.client.get(
            reverse(
                "news:comment-update",
                args=[self.post.pk, self.comment.pk],
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "news/comment-form.html")
        self.assertEqual(response.context["form"].instance, self.comment)
        self.assertContains(response, "Edit your comment")
        self.assertContains(response, self.comment.body)
        self.assertContains(response, 'name="csrfmiddlewaretoken"')

    def test_owner_update_preserves_relationships_and_returns_to_moderation(self):
        replacement_post = Post.objects.create(
            title="Tampered post",
            summary="Tampered summary.",
            article_url="https://example.com/tampered",
            content="Tampered context.",
            author=self.owner,
            category=self.post.category,
            status=Post.Status.PUBLISHED,
        )
        submitted_author = get_user_model().objects.create_user(
            username="submitted-comment-author",
            password="Existing-passphrase-284!",
        )
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse(
                "news:comment-update",
                args=[self.post.pk, self.comment.pk],
            ),
            {
                "body": "Comment after editing.",
                "author": submitted_author.pk,
                "post": replacement_post.pk,
                "is_approved": True,
            },
            follow=True,
        )

        self.comment.refresh_from_db()
        self.assertEqual(self.comment.body, "Comment after editing.")
        self.assertEqual(self.comment.author, self.owner)
        self.assertEqual(self.comment.post, self.post)
        self.assertFalse(self.comment.is_approved)
        detail_url = reverse("news:post-detail", args=[self.post.pk])
        self.assertRedirects(
            response,
            f"{detail_url}#comment-{self.comment.pk}",
        )
        self.assertContains(
            response,
            "Your updated comment is awaiting moderation.",
        )
        self.assertContains(response, "Comment after editing.")

    def test_invalid_update_preserves_input_and_existing_comment(self):
        self.client.force_login(self.owner)
        excessive_body = "x" * 2001

        response = self.client.post(
            reverse(
                "news:comment-update",
                args=[self.post.pk, self.comment.pk],
            ),
            {"body": excessive_body},
        )

        self.comment.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"],
            "body",
            "Ensure this value has at most 2000 characters (it has 2001).",
        )
        self.assertContains(response, excessive_body)
        self.assertContains(response, 'aria-invalid="true"')
        self.assertContains(
            response,
            'aria-describedby="body-help body-error"',
        )
        self.assertContains(response, 'id="body-error"')
        self.assertEqual(self.comment.body, "Comment before editing.")
