from django.test import TestCase
from django.urls import reverse


class LoginPageTests(TestCase):
    def test_login_page_has_expected_accessible_fields(self):
        response = self.client.get(reverse("accounts:login"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")
        self.assertEqual(
            list(response.context["form"].fields),
            ["username", "password"],
        )
        self.assertContains(response, 'method="post"')
        self.assertContains(response, 'name="csrfmiddlewaretoken"')
        self.assertContains(response, '<label for="id_username"')
        self.assertContains(response, '<label for="id_password"')
