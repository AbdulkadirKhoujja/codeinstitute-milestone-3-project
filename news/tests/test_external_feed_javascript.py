from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class ExternalFeedJavascriptTests(SimpleTestCase):
    def test_script_starts_only_for_feed_and_manages_loading_state(self):
        script_path = Path(
            settings.BASE_DIR,
            "static",
            "js",
            "external-feed.js",
        )
        script = script_path.read_text(encoding="utf-8")

        self.assertIn('document.querySelector("#external-feed")', script)
        self.assertIn("if (feed)", script)
        self.assertIn("fetch(feed.dataset.feedUrl", script)
        self.assertIn('setAttribute("aria-busy", "true")', script)
        self.assertIn('removeAttribute("aria-busy")', script)
        self.assertIn("refreshButton.disabled = true", script)
        self.assertIn("refreshButton.disabled = false", script)

    def test_script_renders_untrusted_story_fields_with_safe_dom_methods(self):
        script_path = Path(
            settings.BASE_DIR,
            "static",
            "js",
            "external-feed.js",
        )
        script = script_path.read_text(encoding="utf-8")

        self.assertIn("document.createElement", script)
        self.assertIn("textContent", script)
        self.assertIn("new URL", script)
        self.assertIn('protocol === "https:"', script)
        self.assertIn('protocol === "http:"', script)
        self.assertIn('target = "_blank"', script)
        self.assertIn('rel = "noopener noreferrer"', script)
        self.assertIn("discussion_url", script)
        self.assertIn("submitted_by", script)
        self.assertIn("comment_count", script)
        self.assertNotIn("innerHTML", script)
