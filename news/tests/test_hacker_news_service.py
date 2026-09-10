from unittest.mock import MagicMock
from unittest.mock import patch
from urllib.error import URLError

from django.conf import settings
from django.test import SimpleTestCase
from django.test import override_settings

from news.services.hacker_news import ExternalFeedError
from news.services.hacker_news import fetch_story
from news.services.hacker_news import fetch_top_story_ids
from news.services.hacker_news import normalise_story


class HackerNewsRequestTests(SimpleTestCase):
    @patch("news.services.hacker_news.urlopen")
    def test_oversized_response_is_rejected_before_json_decoding(self, opener):
        from news.services.hacker_news import _request_json

        response = MagicMock()
        response.status = 200
        response.read.return_value = b'"' + b"a" * 131072 + b'"'
        opener.return_value.__enter__.return_value = response
        with self.assertRaises(ExternalFeedError):
            _request_json("item/1.json")

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
        self.assertNotIn("Authorization", request.headers)

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

    @patch("news.services.hacker_news.urlopen")
    def test_timeout_and_network_errors_are_translated(self, mocked_urlopen):
        for failure in (TimeoutError(), URLError("offline")):
            with self.subTest(failure=type(failure).__name__):
                mocked_urlopen.side_effect = failure

                with self.assertRaises(ExternalFeedError):
                    fetch_top_story_ids()

    @patch("news.services.hacker_news.urlopen")
    def test_non_success_and_malformed_json_responses_are_translated(
        self,
        mocked_urlopen,
    ):
        response = MagicMock()
        mocked_urlopen.return_value.__enter__.return_value = response
        for status, body in ((503, b"[]"), (200, b"not-json")):
            with self.subTest(status=status, body=body):
                response.status = status
                response.read.return_value = body

                with self.assertRaises(ExternalFeedError):
                    fetch_top_story_ids()

    @patch("news.services.hacker_news._request_json")
    def test_top_story_id_payload_is_validated(self, mocked_request):
        mocked_request.return_value = {"unexpected": "shape"}
        with self.assertRaises(ExternalFeedError):
            fetch_top_story_ids()

        mocked_request.return_value = ["1", 0, True, 3]
        self.assertEqual(fetch_top_story_ids(), [3])


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
        for external_url in (
            None,
            "",
            "javascript:alert(1)",
            "ftp://host/file",
            "http://[invalid-host",
        ):
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
            self.story_item(time=10**30),
        )

        for item in invalid_items:
            with self.subTest(item=item):
                self.assertIsNone(normalise_story(item))

    def test_unexpected_score_and_comment_types_use_predictable_zeroes(self):
        story = normalise_story(
            self.story_item(score={"unexpected": True}, descendants="many")
        )

        self.assertEqual(story["score"], 0)
        self.assertEqual(story["comment_count"], 0)


class HackerNewsCollectionTests(SimpleTestCase):
    @patch("news.services.feed_worker.fetch_story")
    @patch("news.services.feed_worker.fetch_top_story_ids")
    def test_bounded_collection_respects_target_and_keeps_rank_metadata(
        self, ids, story,
    ):
        from news.services.feed_worker import collect_items
        from news.services.hacker_news import get_story_limit

        ids.return_value = list(range(1, 61))
        story.side_effect = lambda story_id, **kwargs: {"id": story_id}
        for configured, expected in ((30, 30), (5, 20), (99, 50), ("bad", 30)):
            with self.subTest(configured=configured):
                story.reset_mock()
                events = []
                with override_settings(HACKER_NEWS_STORY_LIMIT=configured):
                    collect_items(events.append, get_story_limit(), 5, 5)
                self.assertEqual(story.call_count, expected)
                items = sorted(
                    (event[1], event[2]["id"]) for event in events
                    if event[0] == "item"
                )
                self.assertEqual(items, list(
                    enumerate(range(1, expected + 1))))
                self.assertEqual(events[-1], ("done",))

    @patch("news.services.feed_worker.fetch_story")
    @patch("news.services.feed_worker.fetch_top_story_ids")
    def test_collection_reports_failed_filtered_and_empty_items(
        self, ids, story,
    ):
        from news.services.feed_worker import collect_items

        ids.return_value = [11, 22, 33]

        def fetch(story_id, **kwargs):
            if story_id == 22:
                raise ExternalFeedError("simulated")
            return {"id": 11} if story_id == 11 else None

        story.side_effect = fetch
        events = []
        collect_items(events.append, 30, 5, 5)
        self.assertIn(("failure", 1), events)
        self.assertIn(("item", 2, None), events)
        self.assertIn(("item", 0, {"id": 11}), events)
        self.assertEqual(events[-1], ("done",))
        ids.return_value = []
        story.reset_mock()
        events.clear()
        collect_items(events.append, 30, 5, 5)
        self.assertEqual(events, [("target", 0), ("done",)])
        story.assert_not_called()
