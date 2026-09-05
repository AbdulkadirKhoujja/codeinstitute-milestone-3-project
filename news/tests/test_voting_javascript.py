from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from news.models import Category
from news.models import Post


class VotingJavascriptTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.member = get_user_model().objects.create_user(
            username="javascript-voter",
            password="Existing-passphrase-284!",
        )
        author = get_user_model().objects.create_user(
            username="javascript-author",
            password="Existing-passphrase-284!",
        )
        category = Category.objects.create(
            name="JavaScript voting",
            slug="javascript-voting",
            description="Progressively enhanced voting.",
        )
        cls.post = Post.objects.create(
            title="A progressively enhanced story",
            summary="JavaScript voting summary.",
            article_url="https://example.com/javascript-voting",
            content="JavaScript voting context.",
            author=author,
            category=category,
            status=Post.Status.PUBLISHED,
        )

    def test_story_detail_loads_deferred_voting_script(self):
        self.client.force_login(self.member)

        response = self.client.get(
            reverse("news:post-detail", args=[self.post.pk])
        )

        self.assertContains(response, 'src="/static/js/voting.js"')
        self.assertContains(response, "defer")

    def test_voting_script_uses_safe_progressive_enhancement(self):
        script_path = Path(settings.BASE_DIR, "static", "js", "voting.js")
        script = script_path.read_text(encoding="utf-8")

        self.assertIn("fetch(", script)
        self.assertIn("FormData", script)
        self.assertIn("X-CSRFToken", script)
        self.assertIn("textContent", script)
        self.assertIn("aria-pressed", script)
        self.assertIn("disabled", script)
        self.assertNotIn("innerHTML", script)

    def test_vote_controls_have_clear_active_and_responsive_styles(self):
        stylesheet_path = Path(settings.BASE_DIR, "static", "css", "style.css")
        stylesheet = stylesheet_path.read_text(encoding="utf-8")

        self.assertIn(".vote-panel", stylesheet)
        self.assertIn(".vote-controls", stylesheet)
        self.assertIn('[aria-pressed="true"]', stylesheet)
        self.assertIn(".vote-feedback", stylesheet)
