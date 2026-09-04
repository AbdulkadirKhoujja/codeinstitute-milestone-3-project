from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


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
