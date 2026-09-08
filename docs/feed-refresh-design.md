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

The upstream refresh duration is strictly shorter than the lease. The public
service now calls this shared helper with the bounded worker. Unit tests
establish sequential and re-entrant behaviour; they do not alone establish
actual PostgreSQL cross-process correctness.

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

## Bounded upstream worker

A refresh uses one disposable spawned process containing at most five request
threads. The default overall budget is ten seconds, including startup, followed
by at most half a second of parent cleanup. Each request has a five-second
socket timeout and a 128 KiB response limit; at most 50 item requests are queued.
There are no retries. Completed results retain their original upstream rank.
Incomplete collections are marked partial; no usable results means unavailable.

The separate process is necessary because cancelling a thread future cannot
stop a running socket read, and executor shutdown normally waits for threads.
The parent terminates the process at its deadline. A child watchdog also exits
that disposable process if the requesting web worker has disappeared. The
ten-second default leaves headroom beneath the configured 20-second Gunicorn
worker timeout and Heroku's documented 30-second initial response deadline.
This adds process-startup overhead but does not require another service.

New tests initially failed for the missing worker, oversized responses, startup
cleanup and pipe-creation failure. Following fixes, 30 worker, request and cache
tests passed in 1.135 seconds on Windows. Network responses were mocked. One
test spawned a real blocked child without networking and verified termination
within 2.5 seconds for a one-second budget, with no remaining active child.

A separate live Windows measurement on 8 September 2026 requested and attempted
30 items, returned 30 valid results in 6.750 seconds, with zero failed items and
no partial flag. This measures the worker only, not the shared-cache endpoint;
it is a single observation, not a performance guarantee. Endpoint integration
and cross-process PostgreSQL evidence remain to be recorded.

## Public service integration

The new integration test failed when the public service still attempted the
old sequential HTTP path. After routing through the shared snapshot and worker,
the same test passed: two calls produced one refresh and one database snapshot,
preserving the partial flag. The old process-local cache implementation was
removed. Its cache assertions are replaced by database-backed expiry/cooldown
tests, and collection tests now execute the fixed request pool with mocked HTTP
helpers. Worker, request, shared-cache, feed and script-contract regressions:
44 tests passed in 31.512 seconds on SQLite. These script-contract checks remain
distinct from the separately recorded JavaScript interaction tests.
