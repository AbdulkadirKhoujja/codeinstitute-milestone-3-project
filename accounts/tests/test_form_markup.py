from collections import Counter
from html.parser import HTMLParser

from django.test import TestCase
from django.urls import reverse


class FormMarkup(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.ids = []
        self.references = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if "id" in attributes:
            self.ids.append(attributes["id"])
        self.references.extend(attributes.get("aria-describedby", "").split())


class AccountFormMarkupTests(TestCase):
    def assert_associations(self, response):
        markup = FormMarkup(response.content.decode())
        counts = Counter(markup.ids)
        self.assertTrue(markup.references)
        for reference in markup.references:
            self.assertEqual(counts[reference], 1, reference)
        self.assertFalse([key for key, count in counts.items() if count > 1])

    def test_required_login_errors_have_existing_descriptions(self):
        self.assert_associations(self.client.post(reverse("accounts:login"), {}))

    def test_multiple_password_errors_share_one_description_container(self):
        response = self.client.post(reverse("accounts:register"), {
            "username": "sample-reader", "password1": "123", "password2": "123",
        })
        self.assertGreater(len(response.context["form"].errors["password2"]), 1)
        self.assert_associations(response)
