from html.parser import HTMLParser
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from news.models import Post


class MarkupFacts(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.times = []
        self.labelled_divs = []
        self.in_comment = False
        self.comment_headings = 0
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "time":
            self.times.append(attrs["datetime"])
        if tag == "div" and "aria-label" in attrs:
            self.labelled_divs.append(attrs)
        if tag == "article" and attrs.get("class") == "comment-card":
            self.in_comment = True
        if self.in_comment and tag in {"h2", "h3", "h4", "h5", "h6"}:
            self.comment_headings += 1

    def handle_endtag(self, tag):
        if tag == "article":
            self.in_comment = False


class RenderedMarkupTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_local_samples", confirm_disposable=True,
                     stdout=StringIO())
        cls.member = get_user_model().objects.get(username="sample-editor")
        cls.post = Post.objects.get(title__startswith="[Sample] A practical")

    def pages(self):
        self.client.force_login(self.member)
        for path in ("/", f"/posts/{self.post.pk}/",
                     "/accounts/profile/sample-editor/"):
            yield MarkupFacts(self.client.get(path).content.decode())

    def test_rendered_timestamps_avoid_invalid_microseconds(self):
        for page in self.pages():
            self.assertTrue(page.times)
            for timestamp in page.times:
                if "T" not in timestamp:
                    self.assertRegex(timestamp, r"^\d{4}-\d{2}-\d{2}$")
                    continue  # A profile's joined date has no time component.
                self.assertRegex(timestamp, r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:"
                                 r"\d{2}(?:Z|[+-]\d{2}:?\d{2})$")

    def test_comment_article_has_an_identifying_heading(self):
        response = self.client.get(f"/posts/{self.post.pk}/")
        self.assertGreater(MarkupFacts(
            response.content.decode()).comment_headings, 0)

    def test_labelled_action_containers_have_a_group_role(self):
        for page in self.pages():
            for attrs in page.labelled_divs:
                self.assertEqual(attrs.get("role"), "group", attrs)
