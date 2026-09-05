from unittest.mock import MagicMock
from unittest.mock import patch

from django.conf import settings
from django.test import SimpleTestCase

from news.services.hacker_news import fetch_top_story_ids


class HackerNewsRequestTests(SimpleTestCase):
    @patch("news.services.hacker_news.urlopen")
    def test_top_story_ids_use_official_endpoint_and_configured_timeout(
        self,
        mocked_urlopen,
    ):
        response = MagicMock()
        response.status = 200
        response.read.return_value = b"[30, 20, 10]"
        mocked_urlopen.return_value.__enter__.return_value = response

        story_ids = fetch_top_story_ids()

        self.assertEqual(story_ids, [30, 20, 10])
        request = mocked_urlopen.call_args.args[0]
        self.assertEqual(
            request.full_url,
            f"{settings.HACKER_NEWS_API_BASE_URL}/topstories.json",
        )
        self.assertEqual(
            mocked_urlopen.call_args.kwargs["timeout"],
            settings.HACKER_NEWS_REQUEST_TIMEOUT,
        )
