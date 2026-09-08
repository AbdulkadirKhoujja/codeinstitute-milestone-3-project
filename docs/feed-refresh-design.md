# Shared feed refresh design

## Database cache and coordination

The `FeedSnapshot` model stores only public, normalised Hacker News metadata.
The authoritative database settings select SQLite locally or PostgreSQL in
production. No process-local cache can establish the production refresh policy.

A small model-backed cache combines JSON results and a refresh lease in one
row. This is chosen over Django's general database cache because refresh
coordination requires an atomic conditional update when an expired lease is
contested. The general cache API does not provide a portable compare-and-swap
operation. There is no additional infrastructure dependency or pickle payload.

1. Read an unexpired result, including an empty list, immediately.
2. Otherwise attempt `UPDATE ... WHERE refresh_after <= now` with a new token.
3. Exactly one caller wins. Others return the newly available snapshot or a
   controlled unavailable response; they do not make upstream requests.
4. Keep the next-refresh boundary after success or failure. A successful result
   expires 60 seconds after completion. Failure retries must wait 60 seconds
   from acquisition.
5. Publish only if the caller still owns the token and its lease has not expired.
   An expired worker cannot overwrite a newer refresh. Never serve stale data.

The upstream refresh duration must be strictly shorter than the lease. The
public endpoint is not switched to this helper until the bounded worker is
implemented and tested. Unit tests establish sequential and re-entrant behaviour;
they do not alone establish actual PostgreSQL cross-process correctness.

Setup is the normal `python manage.py migrate` command. There is one lazily
created `hacker-news` row, updated in place. No `createcachetable` command or
expiry-cleanup schedule is needed. Database failures fail closed instead of
causing uncoordinated upstream calls. No user, session, draft or comment data is
stored in this table.

## Observed baseline and tests

On 8 September 2026, before the refresh replacement, a real Windows request
using the sequential service, target 30 and 5-second per-request timeout took
9.641 seconds cold and returned 30 valid items without a partial flag. The
same-process warm request was below the displayed timer resolution. These
measurements are not guaranteed performance or cross-process evidence.

The shared-cache tests first failed because the helper did not exist. After
implementation, its controlled-time success/empty/expiry, competing-request,
failure-cooldown and no-stale checks passed alongside the model suite: 27 tests
in 3.404 seconds. Migration drift check passed.

References: [Django caching](https://docs.djangoproject.com/en/5.2/topics/cache/)
and [Heroku request timeout](https://devcenter.heroku.com/articles/request-timeout).
