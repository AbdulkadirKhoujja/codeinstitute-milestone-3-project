from django.test import TestCase
from django.urls import reverse


class HomePageFoundationTests(TestCase):
    def test_home_uses_accessible_shared_page_foundation(self):
        response = self.client.get(reverse("news:home"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "news/post-list.html")
        self.assertContains(response, '<html lang="en">')
        self.assertContains(response, 'charset="utf-8"')
        self.assertContains(response, 'name="viewport"')
        self.assertContains(response, 'href="#main-content"')
        self.assertContains(response, '<main id="main-content"', html=False)
        self.assertContains(response, "bootstrap@5.3.8")
        self.assertContains(response, 'href="/static/css/style.css"')
