from unittest.mock import MagicMock
from unittest.mock import patch

from django.conf import settings
from django.test import SimpleTestCase

from news.services.hacker_news import fetch_story
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

    @patch("news.services.hacker_news.urlopen")
    def test_story_request_uses_item_endpoint_and_normalises_metadata(
        self,
        mocked_urlopen,
    ):
        response = MagicMock()
        response.status = 200
        response.read.return_value = (
            b'{"id": 42, "type": "story", "title": "Useful release", '
            b'"url": "https://example.com/releases/42", "by": "ada", '
            b'"time": 1_700_000_000, "score": 18, "descendants": 7}'
        ).replace(b"_", b"")
        mocked_urlopen.return_value.__enter__.return_value = response

        story = fetch_story(42)

        request = mocked_urlopen.call_args.args[0]
        self.assertEqual(
            request.full_url,
            f"{settings.HACKER_NEWS_API_BASE_URL}/item/42.json",
        )
        self.assertEqual(
            story,
            {
                "id": 42,
                "title": "Useful release",
                "url": "https://example.com/releases/42",
                "source": "example.com",
                "submitted_by": "ada",
                "submitted_at": "2023-11-14T22:13:20+00:00",
                "score": 18,
                "comment_count": 7,
                "discussion_url": "https://news.ycombinator.com/item?id=42",
            },
        )
