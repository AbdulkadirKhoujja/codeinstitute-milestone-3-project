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


class PostUpdateSubmissionTests(TestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(
            username="update-owner",
            password="Existing-passphrase-284!",
        )
        self.other_member = get_user_model().objects.create_user(
            username="unauthorised-editor",
            password="Existing-passphrase-284!",
        )
        self.category = Category.objects.create(
            name="Software Development",
            slug="software-development",
            description="Software engineering stories.",
        )
        self.post = Post.objects.create(
            title="Story before update",
            summary="Summary before update.",
            article_url="https://example.com/before-update",
            content="Context before update.",
            author=self.owner,
            category=self.category,
            status=Post.Status.PUBLISHED,
        )

    def update_data(self, **changes):
        data = {
            "title": "Story after update",
            "summary": "Summary after update.",
            "article_url": "https://example.com/after-update",
            "content": "Context after update.",
            "category": self.category.pk,
            "status": Post.Status.DRAFT,
        }
        data.update(changes)
        return data

    def test_owner_can_update_story_and_change_publication_status(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse("news:post-update", args=[self.post.pk]),
            self.update_data(author=self.other_member.pk),
            follow=True,
        )

        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "Story after update")
        self.assertEqual(self.post.status, Post.Status.DRAFT)
        self.assertEqual(self.post.author, self.owner)
        self.assertRedirects(
            response,
            reverse("news:post-detail", args=[self.post.pk]),
        )
        self.assertContains(response, "Your changes were saved as a draft.")

    def test_invalid_update_retains_values_without_changing_story(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse("news:post-update", args=[self.post.pk]),
            self.update_data(article_url="not-a-url"),
        )

        self.post.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"],
            "article_url",
            "Enter a valid URL.",
        )
        self.assertContains(response, "Story after update")
        self.assertEqual(self.post.title, "Story before update")

    def test_non_owner_cannot_submit_update(self):
        self.client.force_login(self.other_member)

        response = self.client.post(
            reverse("news:post-update", args=[self.post.pk]),
            self.update_data(),
        )

        self.post.refresh_from_db()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.post.title, "Story before update")
