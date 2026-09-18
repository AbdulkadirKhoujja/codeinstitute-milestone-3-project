# Phase 4 security verification

## Executed request-boundary checks — 8 September 2026

The enforced-CSRF client rejected missing tokens and an untrusted Origin
without saving a comment, then accepted the same-origin request with a genuine
token. These tests explicitly use `Client(enforce_csrf_checks=True)`; ordinary
Django test clients alone would not establish CSRF enforcement.

Additional checks confirmed that GET cannot create comments, vote or log out,
and approved hostile comment text is escaped in the public response. Existing
ownership, draft privacy, pending-comment visibility and safe-login-redirect
tests remain part of the full regression suite.

Two newly reproduced defects were corrected:

1. CSRF middleware returned its default page instead of ByteBoard's custom 403.
   The configured failure view now explains verification/session expiry and
   supplies a home link without exposing diagnostic details or token values.
2. The custom 500 page could raise a second database error when navigation
   evaluated the session-backed user. It now renders without request context,
   so the failure page does not depend on session/auth database access.

Both focused tests failed before their fixes. After correction, the security,
error-page and release-settings group passed all 20 tests in 0.347 seconds on
SQLite. The 500 reproduction uses an isolated lazy user that raises a database
exception; there is no intentional public crash endpoint.

This 8 September record did not establish browser security behaviour,
tracked-history secret scanning or hosted HTTPS configuration; the current-state
review below records the later hosted evidence.

## Current-state review — 18 September 2026

A targeted current-tree review found no tracked private-key or common provider
token patterns. Database configuration is environment-driven: `SECRET_KEY` is
required from the environment, and `DATABASE_URL` is parsed only when supplied.
`.gitignore` excludes local `env.py`, `.env`, local settings and SQLite files.
The tracked `.env.example` and release-settings test contain configuration
examples, not deployed secret values.

`DEBUG`, `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` are environment-driven.
Secure session/CSRF cookies follow non-debug mode; proxy trust is opt-in for
Heroku, HTTPS redirect is explicitly configured, and PostgreSQL SSL requirement
is environment-controlled. Existing enforced-CSRF, ownership/privacy and
anonymous permission tests remain recorded above. The hosted smoke check
separately verifies HTTPS, authentication and the anonymous permission boundary.

No current-state configuration defect was found. Git-history secret scanning
has not been performed and remains a separate review; focused verification
results are recorded below.

## Focused security verification — 18 September 2026

`python manage.py check --deploy` ran with an ephemeral non-production
`SECRET_KEY`, `DEBUG=false`, the live host/origin, and Heroku proxy, HTTPS
redirect and database-SSL flags enabled. It reported two warnings: `security.W004`
because HSTS remains intentionally deferred pending a final-domain policy, and
`security.W009` because the deliberately ephemeral review key did not meet
production key-strength guidance. Neither warning was an application defect in
this review.

Twenty-nine focused tests passed: release settings, enforced CSRF, safe login
redirects, login/logout methods, owner-only comments and drafts, post-owner
actions, proxy handling and database configuration. No security defect was
found. Current-tree security verification is complete for the approved scope;
Git-history secret scanning remains a separate, unperformed review.
