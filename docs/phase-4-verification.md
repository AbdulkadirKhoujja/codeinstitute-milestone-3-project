# Phase 4 verification record

## Baseline — 8 September 2026

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

## Initial evidence gaps

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

## Environment availability

The supported browser connection returned “No browser is available”; the
prescribed discovery check returned an empty list. Browser checks and genuine
screenshots remain unexecuted, not passed. A browser session has been requested.

No Windows PostgreSQL command or service was found. Docker Desktop is installed
but its Linux engine was not running. Existing Ubuntu/WSL infrastructure is
being checked before adding another database installation.

## Corrective testing

| Defect | Reproduction and cause | Correction and retest |
| --- | --- | --- |
| Empty comment edit silently redisplayed the original body | Focused test failed: form was unbound; an empty POST dictionary was treated as a GET | Bind according to request method; required-body error is now returned without changing the record. Comment update/permission suites: 9 tests passed. |

## Release decision

**In progress; not ready for deployment.** Material browser, PostgreSQL,
production-configuration and feed-refresh verification remains outstanding.
No grade or complete accessibility claim is made.
