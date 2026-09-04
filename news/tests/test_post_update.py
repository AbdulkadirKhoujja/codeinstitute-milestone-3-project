from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from news.models import Category
from news.models import Post


class PostUpdatePageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = get_user_model().objects.create_user(
            username="story-owner",
            password="Existing-passphrase-284!",
        )
        cls.other_member = get_user_model().objects.create_user(
            username="other-editor",
            password="Existing-passphrase-284!",
        )
        category = Category.objects.create(
            name="Cybersecurity",
            slug="cybersecurity",
            description="Cybersecurity stories.",
        )
        cls.post = Post.objects.create(
            title="Original story title",
            summary="Original story summary.",
            article_url="https://example.com/original",
            content="Original story context.",
            author=cls.owner,
            category=category,
            status=Post.Status.PUBLISHED,
        )

    def test_anonymous_visitor_is_redirected_to_login(self):
        update_url = reverse("news:post-update", args=[self.post.pk])

        response = self.client.get(update_url)

        self.assertRedirects(
            response,
            f'{reverse("accounts:login")}?next={update_url}',
        )

    def test_owner_receives_prepopulated_edit_form(self):
        self.client.force_login(self.owner)

        response = self.client.get(
            reverse("news:post-update", args=[self.post.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "news/post-form.html")
        self.assertContains(response, "Edit your story")
        self.assertContains(response, self.post.title)
        self.assertEqual(response.context["form"].instance, self.post)

    def test_non_owner_receives_not_found(self):
        self.client.force_login(self.other_member)

        response = self.client.get(
            reverse("news:post-update", args=[self.post.pk])
        )

        self.assertEqual(response.status_code, 404)
