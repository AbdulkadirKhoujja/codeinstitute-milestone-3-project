"""Bound public upstream work, including stuck reads and thread shutdown."""

import multiprocessing
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock, Timer
from time import monotonic

from django.conf import settings

from .hacker_news import (
    ExternalFeedError, StoryCollection, fetch_story, fetch_top_story_ids,
    get_story_limit,
)


def collect_items(send, limit, timeout, workers):
    """Use a fixed small pool; send ranked results as each request completes."""
    ids = fetch_top_story_ids(timeout=timeout)[:limit]
    send(("target", len(ids)))

    def fetch(index, story_id):
        send(("attempt", index))
        return fetch_story(story_id, timeout=timeout)

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(fetch, index, story_id): index
            for index, story_id in enumerate(ids)
        }
        for future in as_completed(futures):
            index = futures[future]
            try:
                send(("item", index, future.result()))
            except ExternalFeedError:
                send(("failure", index))
    send(("done",))


def refresh_child(sender, deadline, limit, timeout, workers):
    """The child watchdog also stops work if the requesting parent exits."""
    # Only this disposable child exits. It owns all upstream threads/sockets.
    watchdog = Timer(max(0.01, deadline - monotonic()), os._exit, args=[0])
    watchdog.daemon = True
    watchdog.start()
    send_lock = Lock()

    def send(event):
        # Pipe writes from request threads must not interleave.
        with send_lock:
            sender.send(event)

    try:
        collect_items(send, limit, timeout, workers)
    except (ExternalFeedError, OSError, ValueError):
        send(("error",))
    finally:
        watchdog.cancel()
        sender.close()


def fetch_bounded_stories():
    """Return partial ranked results within ten seconds plus bounded cleanup."""
    budget = min(15, max(1, settings.HACKER_NEWS_REFRESH_BUDGET))
    deadline = monotonic() + budget
    context = multiprocessing.get_context("spawn")
    try:
        receiver, sender = context.Pipe(duplex=False)
    except OSError:
        raise ExternalFeedError("Hacker News worker is unavailable.") from None
    process = context.Process(
        target=refresh_child,
        args=(sender, deadline, get_story_limit(),
              min(5, settings.HACKER_NEWS_REQUEST_TIMEOUT),
              min(5, max(1, settings.HACKER_NEWS_MAX_WORKERS))),
        daemon=True,
    )
    ranked = {}
    attempted = completed = failed = 0
    done = False
    started = False
    target = None
    try:
        process.start()
        started = True
        sender.close()
        while True:
            remaining = deadline - monotonic()
            if remaining <= 0 or not receiver.poll(remaining):
                break
            event = receiver.recv()
            if event[0] == "target":
                target = event[1]
            elif event[0] == "attempt":
                attempted += 1
            elif event[0] == "item":
                completed += 1
                if event[2] is not None:
                    ranked[event[1]] = event[2]
            elif event[0] == "failure":
                completed += 1
                failed += 1
            elif event[0] == "done":
                done = True
                break
            elif event[0] == "error":
                break
    except (EOFError, OSError):
        # Includes the child watchdog closing a pipe at its deadline.
        pass
    finally:
        if started and process.is_alive():
            process.kill()
        if started:
            process.join(timeout=0.5)
        if not process.is_alive():
            process.close()
        receiver.close()
        if not sender.closed:
            sender.close()

    failed += max(0, attempted - completed)
    if not ranked and (not done or failed or target is None):
        raise ExternalFeedError("Hacker News refresh did not complete.")
    return StoryCollection(
        [ranked[index] for index in sorted(ranked)],
        partial=not done or failed > 0, attempted=attempted, failed=failed,
    )
