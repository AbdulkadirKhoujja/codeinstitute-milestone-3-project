from datetime import timedelta
from unittest.mock import Mock, patch

from django.test import TestCase
from django.utils import timezone

from news.models import FeedSnapshot
from news.services.feed_cache import get_shared_feed
from news.services.hacker_news import (
    ExternalFeedError, StoryCollection, get_top_stories,
)


class SharedFeedCacheTests(TestCase):
    @patch("news.services.hacker_news.urlopen", side_effect=OSError("offline"))
    @patch("news.services.feed_worker.fetch_bounded_stories")
    def test_public_service_uses_bounded_worker_and_shared_snapshot(
        self, worker, opener,
    ):
        worker.return_value = StoryCollection([{"id": 9}], partial=True)
        self.assertTrue(get_top_stories().partial)
        self.assertEqual(get_top_stories(), [{"id": 9}])
        worker.assert_called_once()
        opener.assert_not_called()
        self.assertEqual(FeedSnapshot.objects.get().stories, [{"id": 9}])

    def at(self, now, seconds=0):
        return patch(
            "news.services.feed_cache.timezone.now",
            return_value=now + timedelta(seconds=seconds),
        )

    def test_success_and_empty_results_are_reused_for_sixty_seconds(self):
        for stories in (StoryCollection([{"id": 1}]), StoryCollection()):
            with self.subTest(stories=stories):
                FeedSnapshot.objects.all().delete()
                refresh = Mock(return_value=stories)
                now = timezone.now()
                with self.at(now):
                    self.assertEqual(get_shared_feed(refresh), stories)
                with self.at(now, 59):
                    self.assertEqual(get_shared_feed(refresh), stories)
                refresh.assert_called_once()
                with self.at(now, 61):
                    get_shared_feed(refresh)
                self.assertEqual(refresh.call_count, 2)

    def test_reentrant_cold_request_does_not_start_another_refresh(self):
        other_refresh = Mock()

        def refresh():
            with self.assertRaises(ExternalFeedError):
                get_shared_feed(other_refresh)
            return StoryCollection([{"id": 2}], partial=True)

        self.assertTrue(get_shared_feed(refresh).partial)
        self.assertTrue(get_shared_feed(other_refresh).partial)
        other_refresh.assert_not_called()

    def test_failure_cooldown_expires_without_sleeping(self):
        now = timezone.now()
        refresh = Mock(side_effect=ExternalFeedError("simulated failure"))
        with self.at(now):
            for _ in range(2):
                with self.assertRaises(ExternalFeedError):
                    get_shared_feed(refresh)
        refresh.assert_called_once()
        with self.at(now, 61):
            with self.assertRaises(ExternalFeedError):
                get_shared_feed(refresh)
        self.assertEqual(refresh.call_count, 2)

    def test_expired_data_is_not_served_when_refresh_fails(self):
        now = timezone.now()
        with self.at(now):
            get_shared_feed(lambda: StoryCollection([{"id": 3}]))
        with self.at(now, 61):
            with self.assertRaises(ExternalFeedError):
                get_shared_feed(Mock(side_effect=ExternalFeedError()))
