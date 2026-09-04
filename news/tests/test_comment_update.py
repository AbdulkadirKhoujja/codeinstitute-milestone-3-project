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
