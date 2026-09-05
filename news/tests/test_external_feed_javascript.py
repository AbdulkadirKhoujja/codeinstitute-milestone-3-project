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

    def test_script_handles_empty_error_and_user_refresh_states(self):
        script_path = Path(
            settings.BASE_DIR,
            "static",
            "js",
            "external-feed.js",
        )
        script = script_path.read_text(encoding="utf-8")

        self.assertIn("stories.length === 0", script)
        self.assertIn("No external stories are available right now.", script)
        self.assertIn("renderNotice", script)
        self.assertIn('refreshButton.addEventListener("click", loadStories)', script)
        self.assertIn("if (isLoading)", script)
        self.assertIn("External stories are temporarily unavailable.", script)

    def test_script_announces_partial_result_information(self):
        script_path = Path(
            settings.BASE_DIR,
            "static",
            "js",
            "external-feed.js",
        )
        script = script_path.read_text(encoding="utf-8")

        self.assertIn("if (data.partial)", script)
        self.assertIn("data.message", script)
        self.assertIn("external stories loaded", script)

    def test_external_story_cards_have_distinct_responsive_styles(self):
        stylesheet_path = Path(settings.BASE_DIR, "static", "css", "style.css")
        stylesheet = stylesheet_path.read_text(encoding="utf-8")

        self.assertIn(".discovery-page", stylesheet)
        self.assertIn(".external-feed", stylesheet)
        self.assertIn(".external-story", stylesheet)
        self.assertIn(".external-story--notice", stylesheet)
        self.assertIn("grid-template-columns", stylesheet)
