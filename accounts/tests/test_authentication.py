from django.contrib.auth import get_user_model
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


class LoginSubmissionTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="returning-member",
            password="Existing-passphrase-284!",
        )

    def test_valid_credentials_sign_in_user_with_feedback(self):
        response = self.client.post(
            reverse("accounts:login"),
            {
                "username": "returning-member",
                "password": "Existing-passphrase-284!",
            },
            follow=True,
        )

        self.assertRedirects(response, reverse("news:home"))
        self.assertEqual(
            int(self.client.session["_auth_user_id"]),
            self.user.pk,
        )
        self.assertContains(response, "Welcome back, returning-member.")

    def test_invalid_credentials_return_error_without_session(self):
        response = self.client.post(
            reverse("accounts:login"),
            {
                "username": "returning-member",
                "password": "Wrong-passphrase-395!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Please enter a correct username and password.",
        )
        self.assertNotIn("_auth_user_id", self.client.session)


class LoginRedirectTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="redirect-member",
            password="Existing-passphrase-284!",
        )

    def test_internal_next_destination_is_respected(self):
        internal_destination = f'{reverse("news:home")}?sort=new'
        response = self.client.post(
            reverse("accounts:login"),
            {
                "username": "redirect-member",
                "password": "Existing-passphrase-284!",
                "next": internal_destination,
            },
        )

        self.assertRedirects(response, internal_destination)

    def test_external_next_destination_is_rejected(self):
        response = self.client.post(
            reverse("accounts:login"),
            {
                "username": "redirect-member",
                "password": "Existing-passphrase-284!",
                "next": "https://untrusted.example/collect",
            },
        )

        self.assertRedirects(response, reverse("news:home"))

    def test_authenticated_member_is_redirected_from_login_page(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("accounts:login"))

        self.assertRedirects(response, reverse("news:home"))


class LogoutTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="departing-member",
            password="Existing-passphrase-284!",
        )
        self.client.force_login(self.user)

    def test_post_logs_out_member_with_feedback(self):
        response = self.client.post(reverse("accounts:logout"), follow=True)

        self.assertRedirects(response, reverse("news:home"))
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertContains(response, "You have been logged out.")

    def test_get_does_not_log_out_member(self):
        response = self.client.get(reverse("accounts:logout"))

        self.assertEqual(response.status_code, 405)
        self.assertEqual(
            int(self.client.session["_auth_user_id"]),
            self.user.pk,
        )
