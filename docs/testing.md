# Testing

This document records the Phase 2 testing approach and results that have actually been observed. It does not claim the formal browser, accessibility, performance, validation, production, or deployment evidence scheduled for Phase 4.

## Approach

Phase 2 used short red/green/refactor cycles. A focused test described one behaviour, the test was run to demonstrate the expected failure, the smallest implementation was added, and the focused or directly related tests were run again. Completed slices were then checked with the wider suite before being committed.

Tests use Django's test runner and isolated test database. They create all required users, categories, posts, comments, and votes in the test itself, so results do not depend on a developer's `db.sqlite3`.

## Automated coverage

| Area | Behaviours covered |
| --- | --- |
| Models | Display strings, ordering, required relationships, status choices, deletion rules, vote values, and one-vote-per-user/post integrity |
| Admin | Model registration, list displays, filters, searches, date hierarchy, ordering, and slug prepopulation |
| Shared interface | Home route, shared layout, landmarks, skip link, footer, feedback announcements, and visitor/member navigation states |
| Registration | Expected fields, labels, password help, duplicate username, mismatched passwords, automatic sign-in, feedback, and signed-in visitor redirect |
| Authentication | Valid and invalid credentials, session state, safe internal `next`, rejected external `next`, signed-in visitor redirect, POST logout, and rejected GET logout |
| Profiles | Existing/missing members, non-sensitive public information, published posts, owner management links, owner-only private drafts, and draft privacy |
| Story form | Editable-field allow-list, Bootstrap-compatible widgets, task-specific labels/help, required validation, and URL validation |
| Feed/detail | Published-only listing, query loading, newest ordering, reusable cards, public detail, missing records, owner draft preview, and hidden drafts |
| Story CRUD | Login protection, server-assigned author, draft/published feedback, invalid-value retention, prepopulated updates, deletion confirmation, redirects, ownership, and unsupported methods |
| Discovery | Category filters, named category routes, missing category response, text search, supported/fallback sorting, aggregate positive/negative vote scores, deterministic ordering, pagination, preserved controls, and contextual empty states |

## Representative red-to-green evidence

The following examples describe observed failures before their implementation and the passing behaviour after it. They are representative rather than a transcript of every test command.

| Slice | Initial expected failure | Green behaviour |
| --- | --- | --- |
| Public home | Reversing `news:home` raised `NoReverseMatch` | Root URL renders the shared layout and public feed |
| Registration submit | The initial GET-only page returned an unbound form instead of redirecting after POST | A valid form creates the user, starts a session, redirects, and shows feedback |
| Safe login redirect | A signed-in member received the login page with status `200` | Signed-in members are redirected and external `next` destinations are rejected |
| POST logout | Reversing the logout route raised `NoReverseMatch` | POST ends the session and GET returns `405` |
| Profile draft privacy | An owner draft returned `404` and was absent from the profile | The owner sees a private-drafts section; every other visitor is denied the draft |
| Story feed | Feed tests could not find the expected `posts` context | Only published records are loaded in the required order with related author/category data |
| Story create | A valid POST returned the form page without saving | The story is saved with the signed-in member as author and redirects to detail |
| Ownership | Edit and delete endpoints did not yet exist | Owner operations succeed while another member receives `404` and cannot mutate data |
| Category/search | The unfiltered feed still contained unrelated stories | Filters narrow only published records and preserve active control context |
| Highest rated | `sort=highest` still returned newest order with no aggregate score | Positive and negative vote values are summed and ties use deterministic fallbacks |
| Pagination | A feed fixture returned all 12 stories | Pages contain 10 records and retain category, search, and sort parameters |
| Entry-page links | The login page lacked a create-account link | Registration and login pages now provide explicit reciprocal journeys |
| Story methods | Authenticated `PUT` requests returned the form with status `200` | Create, update, and delete explicitly reject unsupported methods with `405` |

One early template assertion attempted structural HTML comparison on a partial snippet and was corrected to a literal content assertion. A message test also initially attached the wrong storage fixture and was corrected to render with a message instance. These were test-harness corrections, not application defect resolutions.

## Current Phase 2 automated result

The following commands were run from the repository root after the Phase 2 component styling was added:

```text
python manage.py test
Ran 98 tests in 48.028s
OK

python manage.py check
System check identified no issues (0 silenced).

python manage.py makemigrations --check --dry-run
No changes detected
```

The duration is machine-specific. The meaningful result is that all discovered tests passed, Django reported no system-check issue, and the model state had no uncreated migration.

## Manual Phase 2 browser checks

On 4 September 2026, the local Django development server started successfully at `http://127.0.0.1:8000/` and reported no system-check issue. The available in-app browser control was then initialized for the planned visitor/member and responsive pass, but browser discovery returned an empty list. No interactive page, viewport, keyboard, console, or network inspection could therefore be performed in that environment. The server was stopped cleanly and no browser result is claimed.

The unexecuted scope remains visitor and member journeys, narrow and wide responsive states, keyboard focus, navigation state, forms, feedback, CRUD ownership, draft privacy, filters, search, sorting, pagination, console errors, and failed requests. This also does not replace the formal Phase 4 matrix across supported browsers, screen readers, validators, contrast tools, zoom levels, performance tooling, or a deployed environment.

## Later testing

Phase 3 will add focused tests for approved comment display, comment ownership and CRUD, vote creation/change/removal rules, displayed user vote state, and related feedback.

Phase 4 will execute and record the manual functional matrix, browser compatibility, keyboard-only journeys, screen-reader spot checks, contrast, zoom and reflow, HTML/CSS validation, deployment configuration, production migrations, static assets, and development/production parity. Results will be stated only after each check has run.
