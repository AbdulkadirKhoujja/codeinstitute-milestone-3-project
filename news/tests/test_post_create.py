from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from news.models import Category
from news.models import Post


class PostCreatePageTests(TestCase):
    def test_anonymous_visitor_is_redirected_to_login(self):
        response = self.client.get(reverse("news:post-create"))

        expected_url = (
            f'{reverse("accounts:login")}?next={reverse("news:post-create")}'
        )
        self.assertRedirects(response, expected_url)

    def test_member_receives_accessible_story_form(self):
        member = get_user_model().objects.create_user(
            username="story-creator",
            password="Existing-passphrase-284!",
        )
        self.client.force_login(member)

        response = self.client.get(reverse("news:post-create"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "news/post-form.html")
        self.assertContains(response, "Submit a story")
        self.assertContains(response, 'method="post"')
        self.assertContains(response, 'name="csrfmiddlewaretoken"')
        for field_name in (
            "title",
            "summary",
            "article_url",
            "content",
            "category",
            "status",
        ):
            self.assertContains(response, f'for="id_{field_name}"')

    def test_member_cannot_use_unsupported_method(self):
        member = get_user_model().objects.create_user(
            username="method-creator",
            password="Existing-passphrase-284!",
        )
        self.client.force_login(member)

        response = self.client.put(reverse("news:post-create"))

        self.assertEqual(response.status_code, 405)


class PostCreateSubmissionTests(TestCase):
    def setUp(self):
        self.member = get_user_model().objects.create_user(
            username="story-creator",
            password="Existing-passphrase-284!",
        )
        self.other_member = get_user_model().objects.create_user(
            username="injected-author",
            password="Existing-passphrase-284!",
        )
        self.category = Category.objects.create(
            name="Gadgets",
            slug="gadgets",
            description="Device and hardware stories.",
        )
        self.client.force_login(self.member)

    def test_valid_submission_uses_session_owner_and_shows_feedback(self):
        response = self.client.post(
            reverse("news:post-create"),
            {
                "title": "A member-submitted story",
                "summary": "A concise member summary.",
                "article_url": "https://example.com/member-story",
                "content": "Member-provided context.",
                "category": self.category.pk,
                "status": Post.Status.PUBLISHED,
                "author": self.other_member.pk,
            },
            follow=True,
        )

        post = Post.objects.get(title="A member-submitted story")
        self.assertEqual(post.author, self.member)
        self.assertRedirects(
            response,
            reverse("news:post-detail", args=[post.pk]),
        )
        self.assertContains(response, "Your story is now published.")

    def test_invalid_submission_retains_safe_values_without_saving(self):
        response = self.client.post(
            reverse("news:post-create"),
            {
                "title": "Retained story title",
                "summary": "A retained summary.",
                "article_url": "not-a-url",
                "content": "Retained story context.",
                "category": self.category.pk,
                "status": Post.Status.DRAFT,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"],
            "article_url",
            "Enter a valid URL.",
        )
        self.assertContains(response, "Retained story title")
        self.assertEqual(Post.objects.count(), 0)
