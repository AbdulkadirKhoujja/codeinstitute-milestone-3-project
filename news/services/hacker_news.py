"""Small client for the official Hacker News Firebase API."""

import json
from datetime import datetime
from datetime import timezone
from urllib.parse import urlparse
from urllib.request import Request
from urllib.request import urlopen

from django.conf import settings
from django.core.cache import cache


FEED_CACHE_KEY = "byteboard:hacker-news:top-stories:v1"


class ExternalFeedError(Exception):
    """Raised when Hacker News cannot provide usable feed data."""


class StoryCollection(list):
    """List-like feed result carrying a non-sensitive completeness state."""

    def __init__(self, stories=(), *, partial=False):
        super().__init__(stories)
        self.partial = partial


def _request_json(path):
    """Fetch and decode one JSON resource from Hacker News."""
    request = Request(
        f"{settings.HACKER_NEWS_API_BASE_URL}/{path}",
        headers={"User-Agent": "ByteBoard/1.0"},
    )
    try:
        with urlopen(
            request,
            timeout=settings.HACKER_NEWS_REQUEST_TIMEOUT,
        ) as response:
            if response.status != 200:
                raise ExternalFeedError("Hacker News returned an error.")
            return json.loads(response.read().decode("utf-8"))
    except ExternalFeedError:
        raise
    except (OSError, TimeoutError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ExternalFeedError("Hacker News is unavailable.") from error


def fetch_top_story_ids():
    """Return Hacker News top-story identifiers in ranked order."""
    payload = _request_json("topstories.json")
    if not isinstance(payload, list):
        raise ExternalFeedError("Hacker News returned invalid story data.")
    return [
        story_id
        for story_id in payload
        if isinstance(story_id, int)
        and not isinstance(story_id, bool)
        and story_id > 0
    ]


def normalise_story(item):
    """Return the small, presentation-safe subset ByteBoard exposes."""
    if not isinstance(item, dict):
        return None
    story_id = item.get("id")
    title = item.get("title")
    timestamp = item.get("time")
    if (
        not isinstance(story_id, int)
        or isinstance(story_id, bool)
        or story_id < 1
        or not isinstance(title, str)
        or not title.strip()
        or item.get("type") != "story"
        or item.get("dead")
        or item.get("deleted")
        or not isinstance(timestamp, (int, float))
        or isinstance(timestamp, bool)
    ):
        return None

    try:
        submitted_at = datetime.fromtimestamp(
            timestamp,
            tz=timezone.utc,
        ).isoformat()
    except (OSError, OverflowError, ValueError):
        return None

    discussion_url = f"https://news.ycombinator.com/item?id={story_id}"
    external_url = item.get("url")
    try:
        parsed_url = (
            urlparse(external_url) if isinstance(external_url, str) else None
        )
        source = parsed_url.hostname if parsed_url is not None else None
    except ValueError:
        parsed_url = None
        source = None
    if (
        parsed_url is None
        or parsed_url.scheme not in {"http", "https"}
        or not source
    ):
        external_url = discussion_url
        parsed_url = urlparse(external_url)
        source = parsed_url.hostname

    submitted_by = item.get("by")
    if not isinstance(submitted_by, str) or not submitted_by.strip():
        submitted_by = "unknown"
    score = item.get("score")
    if not isinstance(score, int) or isinstance(score, bool):
        score = 0
    comment_count = item.get("descendants")
    if not isinstance(comment_count, int) or isinstance(comment_count, bool):
        comment_count = 0
    return {
        "id": story_id,
        "title": title.strip(),
        "url": external_url,
        "source": source,
        "submitted_by": submitted_by,
        "submitted_at": submitted_at,
        "score": score,
        "comment_count": comment_count,
        "discussion_url": discussion_url,
    }


def fetch_story(story_id):
    """Fetch and normalise one Hacker News story."""
    return normalise_story(_request_json(f"item/{story_id}.json"))


def get_story_limit():
    """Keep the configured refresh size within the product boundary."""
    try:
        configured_limit = int(settings.HACKER_NEWS_STORY_LIMIT)
    except (TypeError, ValueError):
        configured_limit = 30
    return max(20, min(configured_limit, 50))


def get_top_stories():
    """Fetch a bounded set of stories while preserving HN rank order."""
    cached_stories = cache.get(FEED_CACHE_KEY)
    if cached_stories is not None:
        return cached_stories
    story_ids = fetch_top_story_ids()
    stories = StoryCollection()
    failed_requests = 0
    for story_id in story_ids[: get_story_limit()]:
        try:
            story = fetch_story(story_id)
        except ExternalFeedError:
            failed_requests += 1
            continue
        if story is not None:
            stories.append(story)
    if not stories and failed_requests:
        raise ExternalFeedError("Hacker News stories are unavailable.")
    stories.partial = failed_requests > 0
    cache.set(
        FEED_CACHE_KEY,
        stories,
        timeout=settings.HACKER_NEWS_CACHE_TIMEOUT,
    )
    return stories
