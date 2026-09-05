"""Small client for the official Hacker News Firebase API."""

import json
from datetime import datetime
from datetime import timezone
from urllib.parse import urlparse
from urllib.request import Request
from urllib.request import urlopen

from django.conf import settings


def _request_json(path):
    """Fetch and decode one JSON resource from Hacker News."""
    request = Request(
        f"{settings.HACKER_NEWS_API_BASE_URL}/{path}",
        headers={"User-Agent": "ByteBoard/1.0"},
    )
    with urlopen(
        request,
        timeout=settings.HACKER_NEWS_REQUEST_TIMEOUT,
    ) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_top_story_ids():
    """Return Hacker News top-story identifiers in ranked order."""
    return _request_json("topstories.json")


def normalise_story(item):
    """Return the small, presentation-safe subset ByteBoard exposes."""
    story_id = item["id"]
    external_url = item["url"]
    return {
        "id": story_id,
        "title": item["title"],
        "url": external_url,
        "source": urlparse(external_url).hostname,
        "submitted_by": item.get("by", "unknown"),
        "submitted_at": datetime.fromtimestamp(
            item["time"],
            tz=timezone.utc,
        ).isoformat(),
        "score": item.get("score", 0),
        "comment_count": item.get("descendants", 0),
        "discussion_url": (
            f"https://news.ycombinator.com/item?id={story_id}"
        ),
    }


def fetch_story(story_id):
    """Fetch and normalise one Hacker News story."""
    return normalise_story(_request_json(f"item/{story_id}.json"))
