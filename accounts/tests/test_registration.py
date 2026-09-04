from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class RegistrationPageTests(TestCase):
    def test_registration_page_has_expected_accessible_fields(self):
        response = self.client.get(reverse("accounts:register"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/register.html")
        self.assertEqual(
            list(response.context["form"].fields),
            ["username", "password1", "password2"],
        )
        self.assertContains(response, 'method="post"')
        self.assertContains(response, 'name="csrfmiddlewaretoken"')
        self.assertContains(response, '<label for="id_username"')
        self.assertContains(response, '<label for="id_password1"')
        self.assertContains(response, '<label for="id_password2"')
        self.assertContains(response, "Your password must contain")


class RegistrationSubmissionTests(TestCase):
    def test_valid_registration_creates_and_signs_in_user(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "new-member",
                "password1": "Distinctive-passphrase-284!",
                "password2": "Distinctive-passphrase-284!",
            },
            follow=True,
        )

        self.assertRedirects(response, reverse("news:home"))
        self.assertTrue(
            get_user_model().objects.filter(username="new-member").exists()
        )
        self.assertEqual(
            int(self.client.session["_auth_user_id"]),
            get_user_model().objects.get(username="new-member").pk,
        )
        self.assertContains(response, "Welcome to ByteBoard, new-member.")

    def test_duplicate_username_returns_field_error(self):
        get_user_model().objects.create_user(
            username="existing-member",
            password="Existing-passphrase-284!",
        )

        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "existing-member",
                "password1": "Distinctive-passphrase-284!",
                "password2": "Distinctive-passphrase-284!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"],
            "username",
            "A user with that username already exists.",
        )
        self.assertEqual(
            get_user_model().objects.filter(username="existing-member").count(),
            1,
        )

    def test_password_mismatch_returns_field_error(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "new-member",
                "password1": "Distinctive-passphrase-284!",
                "password2": "Different-passphrase-395!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"],
            "password2",
            "The two password fields didn’t match.",
        )
        self.assertFalse(
            get_user_model().objects.filter(username="new-member").exists()
        )
