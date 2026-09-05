from django.test import RequestFactory
from django.test import SimpleTestCase
from django.test import override_settings
from django.urls import reverse

from news.error_views import bad_request
from news.error_views import page_not_found
from news.error_views import permission_denied
from news.error_views import server_error


class CustomErrorPageTests(SimpleTestCase):
    def setUp(self):
        self.request = RequestFactory().get("/unavailable/")

    def assert_error_page(self, response, status_code, heading):
        content = response.content.decode("utf-8")
        self.assertEqual(response.status_code, status_code)
        self.assertIn(heading, content)
        self.assertIn(f'href="{reverse("news:home")}"', content)
        self.assertNotIn("Traceback", content)

    def test_bad_request_page_is_plain_and_navigable(self):
        with self.assertTemplateUsed("400.html"):
            response = bad_request(self.request, Exception("private"))

        self.assert_error_page(response, 400, "We could not process that request")

    def test_permission_denied_page_is_plain_and_navigable(self):
        with self.assertTemplateUsed("403.html"):
            response = permission_denied(self.request, Exception("private"))

        self.assert_error_page(response, 403, "You cannot access this page")

    def test_not_found_page_is_plain_and_navigable(self):
        with self.assertTemplateUsed("404.html"):
            response = page_not_found(self.request, Exception("private"))

        self.assert_error_page(response, 404, "We could not find that page")

    def test_server_error_page_is_plain_and_navigable(self):
        with self.assertTemplateUsed("500.html"):
            response = server_error(self.request)

        self.assert_error_page(response, 500, "Something went wrong")

    @override_settings(DEBUG=False, ALLOWED_HOSTS=["testserver"])
    def test_project_uses_custom_not_found_handler(self):
        response = self.client.get("/a-page-that-does-not-exist/")

        self.assert_error_page(response, 404, "We could not find that page")
        self.assertTemplateUsed(response, "404.html")
