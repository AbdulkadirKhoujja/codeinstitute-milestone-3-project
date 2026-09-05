from unittest.mock import MagicMock
from unittest.mock import patch

from django.conf import settings
from django.test import SimpleTestCase
from django.test import override_settings

from news.services.hacker_news import ExternalFeedError
from news.services.hacker_news import fetch_story
from news.services.hacker_news import fetch_top_story_ids
from news.services.hacker_news import get_top_stories
from news.services.hacker_news import normalise_story


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


class HackerNewsNormalisationTests(SimpleTestCase):
    def story_item(self, **overrides):
        item = {
            "id": 42,
            "type": "story",
            "title": "Fallback link story",
            "by": "grace",
            "time": 1_700_000_000,
            "score": 5,
            "descendants": 2,
        }
        item.update(overrides)
        return item

    def test_missing_or_unsafe_external_url_uses_hn_discussion_url(self):
        for external_url in (None, "", "javascript:alert(1)", "ftp://host/file"):
            with self.subTest(external_url=external_url):
                story = normalise_story(self.story_item(url=external_url))

                self.assertEqual(
                    story["url"],
                    "https://news.ycombinator.com/item?id=42",
                )
                self.assertEqual(story["source"], "news.ycombinator.com")

    def test_malformed_deleted_dead_and_non_story_items_are_ignored(self):
        invalid_items = (
            None,
            {},
            self.story_item(title=""),
            self.story_item(type="job"),
            self.story_item(dead=True),
            self.story_item(deleted=True),
            self.story_item(time="not-a-timestamp"),
        )

        for item in invalid_items:
            with self.subTest(item=item):
                self.assertIsNone(normalise_story(item))


class HackerNewsFeedTests(SimpleTestCase):
    @patch("news.services.hacker_news.fetch_story")
    @patch("news.services.hacker_news.fetch_top_story_ids")
    def test_feed_fetches_default_story_count_in_ranked_order(
        self,
        mocked_ids,
        mocked_story,
    ):
        mocked_ids.return_value = list(range(1, 61))
        mocked_story.side_effect = lambda story_id: {"id": story_id}

        stories = get_top_stories()

        self.assertEqual(
            [story["id"] for story in stories],
            list(range(1, 31)),
        )
        self.assertEqual(mocked_story.call_count, 30)

    @override_settings(HACKER_NEWS_STORY_LIMIT=5)
    @patch("news.services.hacker_news.fetch_story")
    @patch("news.services.hacker_news.fetch_top_story_ids")
    def test_feed_clamps_too_small_limit_to_twenty(
        self,
        mocked_ids,
        mocked_story,
    ):
        mocked_ids.return_value = list(range(1, 61))
        mocked_story.side_effect = lambda story_id: {"id": story_id}

        self.assertEqual(len(get_top_stories()), 20)

    @override_settings(HACKER_NEWS_STORY_LIMIT=99)
    @patch("news.services.hacker_news.fetch_story")
    @patch("news.services.hacker_news.fetch_top_story_ids")
    def test_feed_clamps_too_large_limit_to_fifty(
        self,
        mocked_ids,
        mocked_story,
    ):
        mocked_ids.return_value = list(range(1, 61))
        mocked_story.side_effect = lambda story_id: {"id": story_id}

        self.assertEqual(len(get_top_stories()), 50)

    @patch("news.services.hacker_news.fetch_story")
    @patch("news.services.hacker_news.fetch_top_story_ids")
    def test_feed_keeps_successful_items_when_one_request_fails(
        self,
        mocked_ids,
        mocked_story,
    ):
        mocked_ids.return_value = [11, 22, 33]
        mocked_story.side_effect = (
            {"id": 11},
            ExternalFeedError("item unavailable"),
            {"id": 33},
        )

        self.assertEqual(get_top_stories(), [{"id": 11}, {"id": 33}])

    @patch("news.services.hacker_news.fetch_story")
    @patch("news.services.hacker_news.fetch_top_story_ids")
    def test_feed_reports_failure_when_every_item_request_fails(
        self,
        mocked_ids,
        mocked_story,
    ):
        mocked_ids.return_value = [11, 22]
        mocked_story.side_effect = ExternalFeedError("item unavailable")

        with self.assertRaises(ExternalFeedError):
            get_top_stories()
