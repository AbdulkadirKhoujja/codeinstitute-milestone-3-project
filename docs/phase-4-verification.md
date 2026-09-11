# Phase 4 verification record

## Current recovery baseline — 11 September 2026

Phases 1, 2 and 3 are complete. Phase 4 is underway at verified commit
`4eb7e867cd6ad64a40ad304209d4084f79a3268e`. The read-only recovery audit
confirmed local `main`, cached `origin/main` and GitHub's live `main` matched,
with a clean working tree and zero commits ahead or behind.

| Fresh audit check | Result |
| --- | --- |
| Django tests with isolated settings and in-memory SQLite | 209 passed in 105.755 seconds |
| JavaScript interaction tests | 8 passed |
| JavaScript lint | 5 files; no errors or warnings |
| Python style checks | Passed |
| Django system check | No issues |
| Migration drift | None |
| Git whitespace check | Passed |

Both existing local SQLite databases had news migrations 0001–0005 applied.
The audit used placeholder settings, bypassed private configuration, and did
not alter application data. JavaScript interactions use jsdom and simulated
network responses; the Django suite mocks upstream HTTP. These results do not
establish browser behaviour, accessibility conformance or hosted readiness.

## Completed Phase 4 work and recorded evidence

| Work | Commits | Evidence |
| --- | --- | --- |
| Empty comment-edit and expired-session vote fixes | `c5512a2`, `8f0c034` | Corrective testing below |
| Explicit security settings and PostgreSQL selection | `8e805b4`, `9eddc84` | Settings/database checks below |
| Executable JavaScript checks and malformed-response fixes | `58c5b80` | [Interaction checks](../verification/javascript/README.md) |
| Gunicorn/WhiteNoise and collected static preparation | `6628609` | [Deployment preparation](deployment-preparation.md) |
| Atomic feed snapshot, bounded worker and integration | `e2db3de`, `afc277b`, `441890b` | [Feed design](feed-refresh-design.md) |
| Local PostgreSQL cross-process coordination | `ecca637` | Feed design records a passing simulated-refresh check |
| Form-error associations and guarded sample data | `2d4bb01`, `f4bb35d` | [Form evidence](form-validation-evidence.md), [sample data](local-sample-data.md) |
| CSRF/database-failure pages and rendered markup | `45ab142`, `e8a8574` | [Security](security-verification.md), [validation](formal-validation.md) |
| Staff moderation and edit-warning verification | `0fe91a5` | [Moderation evidence](moderation-verification.md) |
| Python style tooling and formatting | `4eb7e86` | `requirements-dev.txt`, `setup.cfg`; fresh style check passed |

The formal validation record reports 23 rendered HTML samples with zero errors
or warnings on 8 September 2026. This applies to the sampled states at that
time, not all current/future markup or browser-generated DOM. Official CSS
validation remains unresolved: the service returned HTTP 500, not a pass.
The recorded PostgreSQL check uses separate processes and real local database
connections with a simulated refresh; it is not full-suite, load or hosted
verification.

## Browser execution — 11 September 2026

The [manual browser record](manual-browser-verification.md) records actual
local CRUD, authentication, draft privacy, moderation, voting and discovery
journeys across desktop/tablet/mobile presets, plus sampled keyboard checks.
Two feedback defects were corrected and browser-retested in `88be9ba`;
19 focused Django tests and changed-file style/whitespace checks passed.
Browser control then timed out; unchecked variants and interrupted narrow/zoom
checks remain explicit gaps. Screenshots were displayed in-session only.
The earlier HTML result predates the changed story-form markup.

The resumed browser block verified 320px wrapping, further keyboard paths,
script-blocked form voting and controlled discovery failure/empty recovery.
CSS correction `3bb151a` fixes category reflow and measured error-link contrast.
See the same manual record for ratios, fixture limits and remaining gaps;
genuine zoom, screen-reader use and saved screenshots remain unverified.

## Remaining verification and release decision

- Remaining browser journey variants and viewport coverage listed in the manual
  record; fuller keyboard/screen-reader checks, measured contrast, zoom/reflow,
  network inspection, multi-browser coverage and saved assessment screenshots.
- CSS validator retry and final HTML coverage after relevant changes.
- Full current-suite PostgreSQL testing and hosted-runtime, HTTPS, static asset,
  production migration, feed timing and development/production parity checks.
- Final security-history review, performance evidence, credits and submission
  documentation.
- Separate deployment operation and verified live URL.

**In progress; not ready for deployment.** No deployment/live URL, accessibility conformance, CSS validator success or
hosted-runtime pass is recorded. Sampled keyboard checks are documented above.

## Historical baseline — 8 September 2026

Phase 4 covers local verification, corrections, evidence and production
preparation. Heroku deployment is a separate operation and has not occurred.

- Clean `main`; fresh `git fetch origin` succeeded.
- Local and remote baseline: `28114f0a27b35065ab9996ed43b8a97d6852ac91`.
- Ahead/behind: `0 / 0`.
- `python manage.py test`: 173 tests passed in 120.119 seconds on SQLite.
- `python manage.py check`: no issues.
- `python manage.py makemigrations --check --dry-run`: no changes.
- `python manage.py migrate`: no migrations to apply.
- `git diff --check`: clean.
- `env.py`, `.env` and `db.sqlite3` are ignored. No values were printed.
- No applicable repository instruction file was found.

The existing tests verify server behaviour and some source/template structure.
They do not establish browser execution, keyboard usability or conformance.

## Historical initial evidence gaps — 8 September 2026

This table preserves the starting assessment; the completed-work and remaining-verification sections above supersede it as the current status.

The assessment tracker was reviewed against the models, migrations, views,
forms, templates, custom styles/scripts, tests and planning documents.

| Scope | Existing evidence | Remaining verification |
| --- | --- | --- |
| Pass 1.1–1.2, Merit M(i), interface craftsmanship | Semantic templates and original CSS | Actual responsive, keyboard, contrast and accessibility checks |
| Pass 1.3–1.4, 2.1, 3.1; M(x) | Relational models, migrations and CRUD tests | PostgreSQL and manual journeys; publication transitions |
| Pass 1.5–1.6; M(v)–M(vi) | 173 passing tests and historical TDD examples | Executable JavaScript, official validators, style checks and bug retests |
| Pass 1.7–1.10; M(iv) | Conventional Python, templates and filenames | Final code and rendered-markup audit |
| Pass 2.2; M(viii) | Central SQLite settings | Environment-driven PostgreSQL and actual integration run |
| Pass 4.1–4.3; M(xiii) | Planning only | Pending deployment; local preparation cannot complete these |
| Pass 5.1; M(xii) | Independently pushed history | Continue small, green, individually pushed units |
| Pass 5.2–5.4 | Ignored secrets; environment SECRET_KEY | History audit, enforced-CSRF tests, safe production defaults |
| M(ii), M(iii), M(xi) | Purpose-led home, feedback and CRUD responses | Browser feedback, failure recovery and progressive enhancement |
| M(vii), M(xiv) | README schema, purpose, permissions and rationale | Final implementation alignment and known limitations |
| M(ix) | Pinned Python requirements | Runtime, Procfile, static serving and clean installation |
| Distinction lifecycle and defensive design | Planning, implementation and automated evidence | Bounded feed refresh, shared coordination, release evidence |

## Historical environment availability — 8 September 2026

The supported browser connection returned “No browser is available”; the
prescribed discovery check returned an empty list. Browser checks and genuine
screenshots remain unexecuted, not passed. A browser session has been requested.

No Windows PostgreSQL command or service was found. Docker Desktop is installed
but its Linux engine was not running. Existing Ubuntu/WSL infrastructure is
being checked before adding another database installation at that point. The later PostgreSQL installation and cross-process result are recorded below and in the feed design.

## Corrective testing

| Defect | Reproduction and cause | Correction and retest |
| --- | --- | --- |
| Empty comment edit silently redisplayed the original body | Focused test failed: form was unbound; an empty POST dictionary was treated as a GET | Bind according to request method; required-body error is now returned without changing the record. Comment update/permission suites: 9 tests passed. |
| Expired-session form voting returned to an unusable page after login | Focused test received 405 instead of 200: login returned to the POST-only vote endpoint | Return to the story detail page without replaying a mutation. Voting suite: 17 tests passed. |

## Production-settings verification

Five isolated settings tests initially failed because debug was always on,
cookie/proxy controls were absent, and missing or malformed configuration did
not fail at startup. Settings now parse explicit booleans and lists, require a
secret, disable debug by default, secure cookies outside debug and require
explicit proxy trust. HSTS remains zero pending final-domain verification.
The local private DEBUG value was not a supported boolean; test commands use
an explicit process environment value without rewriting private configuration.
Settings, account and custom-error suites: 29 tests passed in 14.761 seconds.

## Database configuration

Three new settings tests reproduced the missing PostgreSQL URL selection,
disposable SQLite path and safe malformed-URL handling. The corrected settings
and model suites passed 31 tests in 3.466 seconds, with no migration drift.
The Windows virtual environment installed the pinned stack, database-URL parser
and Psycopg successfully; `pip check` found no broken requirements.
`requirements.txt` was normalised from UTF-16 to UTF-8 for portable text tooling.

PostgreSQL 18.6 was installed in the existing Ubuntu environment. Before test
data preparation its cluster contained only postgres/template0/template1.
That initial installation established availability only. The later passing local
PostgreSQL cross-process cache check is recorded in [feed refresh design](feed-refresh-design.md).
Full current-suite PostgreSQL and hosted-runtime verification remain outstanding;
the current release decision is recorded above.
