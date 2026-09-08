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

This record does not yet establish browser security behaviour, tracked-history
secret scanning or hosted HTTPS configuration. Those require separate evidence.
