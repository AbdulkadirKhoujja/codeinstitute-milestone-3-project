from django.conf import settings
from django.test import SimpleTestCase


class HackerNewsSettingsTests(SimpleTestCase):
    def test_integration_defaults_are_centralised_and_bounded(self):
        self.assertEqual(
            settings.HACKER_NEWS_API_BASE_URL,
            "https://hacker-news.firebaseio.com/v0",
        )
        self.assertEqual(settings.HACKER_NEWS_STORY_LIMIT, 30)
        self.assertGreaterEqual(settings.HACKER_NEWS_STORY_LIMIT, 20)
        self.assertLessEqual(settings.HACKER_NEWS_STORY_LIMIT, 50)
        self.assertEqual(settings.HACKER_NEWS_CACHE_TIMEOUT, 60)
        self.assertGreater(settings.HACKER_NEWS_REQUEST_TIMEOUT, 0)
