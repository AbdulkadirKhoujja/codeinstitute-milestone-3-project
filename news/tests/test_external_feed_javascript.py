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
