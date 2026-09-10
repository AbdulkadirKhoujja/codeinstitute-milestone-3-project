import multiprocessing
from time import monotonic
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase, override_settings

from news.services.feed_worker import fetch_bounded_stories
from news.services.hacker_news import ExternalFeedError


def blocked_test_child(*args):
    """A local child with no HTTP activity, killed by the parent deadline."""
    multiprocessing.Event().wait()


@override_settings(HACKER_NEWS_REFRESH_BUDGET=10)
class FeedWorkerTests(SimpleTestCase):
    def worker_context(self, events):
        context = MagicMock()
        receiver, sender = MagicMock(), MagicMock()
        context.Pipe.return_value = (receiver, sender)
        receiver.poll.return_value = True
        receiver.recv.side_effect = events
        return context, receiver, sender

    @patch("news.services.feed_worker.multiprocessing.get_context")
    def test_out_of_order_results_keep_rank_and_report_partial(self, factory):
        context, receiver, sender = self.worker_context([
            ("target", 3), ("attempt", 0), ("attempt", 1), ("attempt", 2),
            ("item", 2, {"id": 3}), ("failure", 1),
            ("item", 0, {"id": 1}), ("done",),
        ])
        factory.return_value = context
        stories = fetch_bounded_stories()
        self.assertEqual(stories, [{"id": 1}, {"id": 3}])
        self.assertTrue(stories.partial)
        self.assertEqual(stories.attempted, 3)
        self.assertEqual(stories.failed, 1)
        context.Process.return_value.join.assert_called_with(timeout=0.5)
        receiver.close.assert_called_once()
        sender.close.assert_called_once()

    @patch("news.services.feed_worker.multiprocessing.get_context")
    def test_deadline_terminates_worker_without_thread_wait(self, factory):
        context, receiver, sender = self.worker_context([
            ("target", 30), ("attempt", 0), ("item", 0, {"id": 1}),
        ])
        receiver.poll.side_effect = [True, True, True, False]
        factory.return_value = context
        stories = fetch_bounded_stories()
        self.assertEqual(stories, [{"id": 1}])
        self.assertTrue(stories.partial)
        context.Process.return_value.kill.assert_called_once()
        context.Process.return_value.join.assert_called_with(timeout=0.5)
        self.assertLessEqual(receiver.poll.call_args.args[0], 10)

    @patch("news.services.feed_worker.multiprocessing.get_context")
    def test_no_results_before_budget_is_a_controlled_failure(self, factory):
        context, receiver, sender = self.worker_context([])
        receiver.poll.return_value = False
        factory.return_value = context
        with self.assertRaises(ExternalFeedError):
            fetch_bounded_stories()
        context.Process.return_value.kill.assert_called_once()

    @patch("news.services.feed_worker.multiprocessing.get_context")
    def test_empty_completed_upstream_is_a_success(self, factory):
        context, receiver, sender = self.worker_context([
            ("target", 0), ("done",),
        ])
        factory.return_value = context
        stories = fetch_bounded_stories()
        self.assertEqual(stories, [])
        self.assertFalse(stories.partial)

    @patch("news.services.feed_worker.multiprocessing.get_context")
    def test_start_failure_is_controlled_without_joining_unstarted_process(
        self, factory,
    ):
        context, receiver, sender = self.worker_context([])
        context.Process.return_value.start.side_effect = OSError("unavailable")
        factory.return_value = context
        with self.assertRaises(ExternalFeedError):
            fetch_bounded_stories()
        context.Process.return_value.join.assert_not_called()

    @patch("news.services.feed_worker.multiprocessing.get_context")
    def test_pipe_creation_failure_is_controlled(self, factory):
        factory.return_value.Pipe.side_effect = OSError("pipe unavailable")
        with self.assertRaises(ExternalFeedError):
            fetch_bounded_stories()

    @override_settings(HACKER_NEWS_REFRESH_BUDGET=1)
    def test_real_blocked_child_is_terminated_without_network(self):
        real_context = multiprocessing.get_context("spawn")
        context = MagicMock()
        context.Pipe.side_effect = real_context.Pipe

        def process_factory(**kwargs):
            kwargs["target"] = blocked_test_child
            return real_context.Process(**kwargs)

        context.Process.side_effect = process_factory
        children_before = {
            child.pid for child in multiprocessing.active_children()}
        started = monotonic()
        with patch("news.services.feed_worker.multiprocessing.get_context",
                   return_value=context):
            with self.assertRaises(ExternalFeedError):
                fetch_bounded_stories()
        self.assertLess(monotonic() - started, 2.5)
        self.assertEqual(
            {child.pid for child in multiprocessing.active_children()},
            children_before,
        )
