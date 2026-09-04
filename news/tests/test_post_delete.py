from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from news.models import Category
from news.models import Post


class PostDeletePageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = get_user_model().objects.create_user(
            username="delete-owner",
            password="Existing-passphrase-284!",
        )
        cls.other_member = get_user_model().objects.create_user(
            username="delete-visitor",
            password="Existing-passphrase-284!",
        )
        category = Category.objects.create(
            name="Technology",
            slug="technology",
            description="General technology stories.",
        )
        cls.post = Post.objects.create(
            title="Story awaiting deletion",
            summary="A story that might be removed.",
            article_url="https://example.com/delete",
            content="Deletion test context.",
            author=cls.owner,
            category=category,
            status=Post.Status.PUBLISHED,
        )

    def test_anonymous_visitor_is_redirected_to_login(self):
        delete_url = reverse("news:post-delete", args=[self.post.pk])

        response = self.client.get(delete_url)

        self.assertRedirects(
            response,
            f'{reverse("accounts:login")}?next={delete_url}',
        )

    def test_owner_receives_explicit_confirmation_form(self):
        self.client.force_login(self.owner)

        response = self.client.get(
            reverse("news:post-delete", args=[self.post.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "news/post-confirm-delete.html")
        self.assertContains(response, self.post.title)
        self.assertContains(response, "cannot be undone")
        self.assertContains(response, 'method="post"')
        self.assertContains(response, 'name="csrfmiddlewaretoken"')
        self.assertContains(response, "Delete story")
        self.assertTrue(Post.objects.filter(pk=self.post.pk).exists())

    def test_non_owner_receives_not_found(self):
        self.client.force_login(self.other_member)

        response = self.client.get(
            reverse("news:post-delete", args=[self.post.pk])
        )

        self.assertEqual(response.status_code, 404)
