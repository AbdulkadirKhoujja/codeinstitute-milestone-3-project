"""Small client for the official Hacker News Firebase API."""

import json
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
