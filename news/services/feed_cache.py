"""Database-backed public feed caching with an atomic refresh boundary."""

from datetime import timedelta
from uuid import uuid4

from django.conf import settings
from django.db import DatabaseError
from django.utils import timezone

from news.models import FeedSnapshot

from .hacker_news import ExternalFeedError, StoryCollection


def cached_collection(snapshot, now):
    """Return only unexpired data; an empty successful feed is cacheable."""
    if (snapshot.stories is not None and snapshot.expires_at is not None
            and snapshot.expires_at > now):
        return StoryCollection(snapshot.stories, partial=snapshot.partial)
    return None


def get_shared_feed(refresh):
    """Share results and failure cooldowns across workers using one DB row."""
    try:
        return _get_shared_feed(refresh)
    except DatabaseError:
        # An unavailable cache must never trigger uncoordinated upstream work.
        raise ExternalFeedError("The feed cache is unavailable.") from None


def _get_shared_feed(refresh):
    now = timezone.now()
    snapshot, _ = FeedSnapshot.objects.get_or_create(
        key="hacker-news", defaults={"refresh_after": now},
    )
    cached = cached_collection(snapshot, now)
    if cached is not None:
        return cached

    token = uuid4()
    # One conditional UPDATE wins even when an expired lease is contested.
    # Do not hold a database transaction open during upstream HTTP requests.
    acquired = FeedSnapshot.objects.filter(
        pk=snapshot.pk, refresh_after__lte=now,
    ).update(
        refresh_after=now + timedelta(
            seconds=settings.HACKER_NEWS_CACHE_TIMEOUT,
        ),
        refresh_token=token,
    )
    if not acquired:
        snapshot.refresh_from_db()
        cached = cached_collection(snapshot, timezone.now())
        if cached is not None:
            return cached
        raise ExternalFeedError("Feed refresh is busy or cooling down.")

    # Keep the lease after failure: retries cannot cause an upstream storm.
    stories = refresh()
    completed = timezone.now()
    saved = FeedSnapshot.objects.filter(
        pk=snapshot.pk, refresh_token=token, refresh_after__gt=completed,
    ).update(
        stories=list(stories), partial=stories.partial,
        expires_at=completed + timedelta(
            seconds=settings.HACKER_NEWS_CACHE_TIMEOUT,
        ),
    )
    if not saved:
        raise ExternalFeedError("The feed refresh lease expired.")
    return stories
