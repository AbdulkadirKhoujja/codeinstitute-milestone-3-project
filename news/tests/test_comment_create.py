from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from news.models import Category
from news.models import Comment
from news.models import Post


class CommentCreationTests(TestCase):
    def setUp(self):
        self.member = get_user_model().objects.create_user(
            username="comment-creator",
            password="Existing-passphrase-284!",
        )
        self.other_member = get_user_model().objects.create_user(
            username="submitted-author",
            password="Existing-passphrase-284!",
        )
        category = Category.objects.create(
            name="Discussion",
            slug="discussion",
            description="Discussion stories.",
        )
        self.post = Post.objects.create(
            title="A commentable story",
            summary="Commentable summary.",
            article_url="https://example.com/commentable",
            content="Commentable context.",
            author=self.other_member,
            category=category,
            status=Post.Status.PUBLISHED,
        )

    def test_detail_shows_member_form_and_visitor_login_guidance(self):
        visitor_response = self.client.get(
            reverse("news:post-detail", args=[self.post.pk])
        )
        self.assertNotContains(visitor_response, 'name="body"')
        self.assertContains(visitor_response, reverse("accounts:login"))
        self.assertContains(visitor_response, "Log in to join the discussion")

        self.client.force_login(self.member)
        member_response = self.client.get(
            reverse("news:post-detail", args=[self.post.pk])
        )
        self.assertEqual(
            list(member_response.context["comment_form"].fields),
            ["body"],
        )
        self.assertContains(member_response, 'name="body"')
        self.assertContains(
            member_response,
            reverse("news:comment-create", args=[self.post.pk]),
        )

    def test_valid_post_creates_server_owned_pending_comment(self):
        self.client.force_login(self.member)

        response = self.client.post(
            reverse("news:comment-create", args=[self.post.pk]),
            {
                "body": "A useful new contribution.",
                "author": self.other_member.pk,
                "post": 9999,
                "is_approved": True,
            },
            follow=True,
        )

        comment = Comment.objects.get(body="A useful new contribution.")
        self.assertEqual(comment.author, self.member)
        self.assertEqual(comment.post, self.post)
        self.assertFalse(comment.is_approved)
        self.assertRedirects(
            response,
            f'{reverse("news:post-detail", args=[self.post.pk])}#comment-{comment.pk}',
        )
        self.assertContains(response, comment.body)
        self.assertContains(response, "Your comment is awaiting moderation.")
