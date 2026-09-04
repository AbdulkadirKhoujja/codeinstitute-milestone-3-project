from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from news.models import Category
from news.models import Comment
from news.models import Post


class CommentPermissionTests(TestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(
            username="permission-owner",
            password="Existing-passphrase-284!",
        )
        self.other_member = get_user_model().objects.create_user(
            username="permission-other",
            password="Existing-passphrase-284!",
        )
        category = Category.objects.create(
            name="Permissions",
            slug="permissions",
            description="Permission stories.",
        )
        self.post = Post.objects.create(
            title="Published permission story",
            summary="Published permission summary.",
            article_url="https://example.com/published-permission",
            content="Published permission context.",
            author=self.owner,
            category=category,
            status=Post.Status.PUBLISHED,
        )
        self.private_post = Post.objects.create(
            title="Private permission story",
            summary="Private permission summary.",
            article_url="https://example.com/private-permission",
            content="Private permission context.",
            author=self.owner,
            category=category,
            status=Post.Status.DRAFT,
        )
        self.comment = Comment.objects.create(
            post=self.post,
            author=self.owner,
            body="Permission-controlled comment.",
            is_approved=True,
        )

    def test_anonymous_comment_actions_redirect_to_login(self):
        urls = (
            reverse("news:comment-create", args=[self.post.pk]),
            reverse(
                "news:comment-update",
                args=[self.post.pk, self.comment.pk],
            ),
            reverse(
                "news:comment-delete",
                args=[self.post.pk, self.comment.pk],
            ),
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.client.post(url, {"body": "Attempted change."})
                self.assertRedirects(
                    response,
                    f'{reverse("accounts:login")}?next={url}',
                )

    def test_non_owner_cannot_edit_or_delete_comment(self):
        self.client.force_login(self.other_member)
        urls = (
            reverse(
                "news:comment-update",
                args=[self.post.pk, self.comment.pk],
            ),
            reverse(
                "news:comment-delete",
                args=[self.post.pk, self.comment.pk],
            ),
        )
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 404)
                self.assertEqual(self.client.post(url).status_code, 404)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.body, "Permission-controlled comment.")

    def test_comment_creation_rejects_missing_and_other_members_draft(self):
        self.client.force_login(self.other_member)
        for post_id in (9999, self.private_post.pk):
            with self.subTest(post_id=post_id):
                response = self.client.post(
                    reverse("news:comment-create", args=[post_id]),
                    {"body": "Inaccessible comment."},
                )
                self.assertEqual(response.status_code, 404)
        self.assertEqual(Comment.objects.count(), 1)

    def test_owner_can_comment_on_own_private_draft(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse("news:comment-create", args=[self.private_post.pk]),
            {"body": "Private drafting note."},
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Comment.objects.filter(
                post=self.private_post,
                author=self.owner,
                body="Private drafting note.",
            ).exists()
        )

    def test_authenticated_unsupported_methods_are_rejected(self):
        self.client.force_login(self.owner)
        create_url = reverse("news:comment-create", args=[self.post.pk])
        update_url = reverse(
            "news:comment-update",
            args=[self.post.pk, self.comment.pk],
        )
        delete_url = reverse(
            "news:comment-delete",
            args=[self.post.pk, self.comment.pk],
        )

        self.assertEqual(self.client.get(create_url).status_code, 405)
        self.assertEqual(self.client.put(update_url).status_code, 405)
        self.assertEqual(self.client.put(delete_url).status_code, 405)
