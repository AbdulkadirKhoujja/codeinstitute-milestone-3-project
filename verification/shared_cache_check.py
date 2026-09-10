"""Offline cross-process check; only the named disposable PostgreSQL DB."""

import json
import os
from pathlib import Path
import selectors
import subprocess
import sys
from unittest.mock import patch

import django


def main():
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "byteboard.settings")
    django.setup()
    from django.db import connection
    from news.models import FeedSnapshot
    from news.services.hacker_news import (
        ExternalFeedError,
        StoryCollection,
        get_top_stories,
    )

    if (connection.vendor != "postgresql"
            or connection.settings_dict["NAME"] != "byteboard_phase4"):
        raise SystemExit("Requires disposable PostgreSQL byteboard_phase4.")

    def sample_refresh():
        print("acquired", flush=True)
        if sys.stdin.readline().strip() != "release":
            raise RuntimeError("Missing release signal")
        return StoryCollection([{"id": 123, "title": "Sample cache check"}])

    if len(sys.argv) == 2 and sys.argv[1] in {"refresh", "read"}:
        replacement = sample_refresh if sys.argv[1] == "refresh" else None
        worker_path = "news.services.feed_worker.fetch_bounded_stories"
        with patch(worker_path) as worker:
            worker.side_effect = replacement or AssertionError(
                "A competing or warm process attempted an upstream refresh"
            )
            try:
                result = get_top_stories()
                print(json.dumps({"status": "cached", "stories": result}))
            except ExternalFeedError:
                print(json.dumps({"status": "busy"}))
        return

    if sys.argv[1:] != ["--confirm-disposable"]:
        raise SystemExit(
            "Use --confirm-disposable; resets one public cache row.")

    FeedSnapshot.objects.filter(pk="hacker-news").delete()
    command = [sys.executable, str(Path(__file__).resolve())]
    processes = []
    try:
        leader = subprocess.Popen(
            command + ["refresh"], stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        processes.append(leader)
        with selectors.DefaultSelector() as selector:
            selector.register(leader.stdout, selectors.EVENT_READ)
            if not selector.select(timeout=45):
                raise AssertionError(
                    "Leader did not acquire within 45 seconds")
        assert leader.stdout.readline().strip() == "acquired"
        followers = [subprocess.Popen(
            command + ["read"], stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True,
        ) for _ in range(4)]
        processes.extend(followers)
        for follower in followers:
            output, errors = follower.communicate(timeout=15)
            assert follower.returncode == 0, errors
            assert json.loads(output) == {"status": "busy"}, output
        output, errors = leader.communicate(input="release\n", timeout=10)
        assert leader.returncode == 0, errors
        assert json.loads(output)["stories"][0]["id"] == 123
        warm = subprocess.run(
            command + ["read"], capture_output=True, text=True,
            timeout=10, check=True,
        )
        assert json.loads(warm.stdout)["stories"][0]["id"] == 123
        assert FeedSnapshot.objects.filter(pk="hacker-news").count() == 1
        print("PASS: one leader, four blocked competitors, separate warm read")
    finally:
        for process in processes:
            if process.poll() is None:
                process.kill()
            process.communicate(timeout=5)
        FeedSnapshot.objects.filter(pk="hacker-news").delete()


if __name__ == "__main__":
    main()
