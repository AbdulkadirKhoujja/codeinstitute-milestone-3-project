from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from news.services.hacker_news import ExternalFeedError
from news.services.hacker_news import StoryCollection


class HackerNewsFeedEndpointTests(TestCase):
    @patch("news.views.get_top_stories")
    def test_same_origin_endpoint_returns_normalised_stories(
        self,
        mocked_feed,
    ):
        stories = [
            {
                "id": 42,
                "title": "A useful external story",
                "url": "https://example.com/story",
                "source": "example.com",
                "submitted_by": "ada",
                "submitted_at": "2023-11-14T22:13:20+00:00",
                "score": 18,
                "comment_count": 7,
                "discussion_url": "https://news.ycombinator.com/item?id=42",
            }
        ]
        mocked_feed.return_value = stories

        response = self.client.get(reverse("news:hacker-news-feed"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"success": True, "stories": stories},
        )
        self.assertEqual(response.headers["Cache-Control"], "no-store")

    @patch("news.views.get_top_stories")
    def test_partial_feed_returns_valid_subset_and_information(
        self,
        mocked_feed,
    ):
        stories = StoryCollection([{"id": 42}], partial=True)
        mocked_feed.return_value = stories

        response = self.client.get(reverse("news:hacker-news-feed"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "success": True,
                "stories": [{"id": 42}],
                "partial": True,
                "message": "Some external stories could not be loaded.",
            },
        )


class HackerNewsDiscoveryPageTests(TestCase):
    def test_discovery_page_exposes_accessible_feed_structure(self):
        response = self.client.get(reverse("news:discover"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "news/discover.html")
        self.assertContains(response, 'id="external-feed"')
        self.assertContains(
            response,
            f'data-feed-url="{reverse("news:hacker-news-feed")}"',
        )
        self.assertContains(response, 'aria-busy="true"')
        self.assertContains(response, 'data-feed-status role="status"')
        self.assertContains(response, 'data-feed-refresh')
        self.assertContains(response, "Powered by the")
        self.assertContains(response, "Hacker News API")
        self.assertContains(response, 'src="/static/js/external-feed.js"')

    @patch("news.views.get_top_stories")
    def test_feed_endpoint_only_accepts_get(self, mocked_feed):
        response = self.client.post(reverse("news:hacker-news-feed"))

        self.assertEqual(response.status_code, 405)
        mocked_feed.assert_not_called()

    @patch("news.views.get_top_stories")
    def test_feed_failure_returns_retryable_structured_response(
        self,
        mocked_feed,
    ):
        mocked_feed.side_effect = ExternalFeedError("private detail")

        response = self.client.get(reverse("news:hacker-news-feed"))

        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.json(),
            {
                "success": False,
                "stories": [],
                "message": (
                    "External stories are temporarily unavailable. "
                    "Please try again."
                ),
            },
        )
        self.assertEqual(response.headers["Cache-Control"], "no-store")
