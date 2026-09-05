# Testing

This document records the Phase 3 testing approach and results that have actually been observed. It does not claim the formal browser, accessibility, performance, validation, production, or deployment evidence scheduled for Phase 4.

## Approach

Phase 3 continued the short red/green/refactor cycles established in Phase 2. A focused test described one behaviour, the test was run to demonstrate the expected failure, the smallest implementation was added, and focused or directly related tests were run again. Each completed green slice was committed and pushed before the next slice.

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
| Community discovery | Category filters, named category routes, missing category response, text search, supported/fallback sorting, aggregate positive/negative vote scores, deterministic ordering, pagination, preserved controls, and contextual empty states |
| Comments | Form allow-list and validation, approved/public and pending/private visibility, server-owned creation, edit-remoderation, deletion confirmation, ownership boundaries, missing records, feedback, and method restrictions |
| Voting | Score display, create/change/remove transitions in both directions, value allow-list, member isolation, authentication, published-only targets, non-JavaScript redirect fallback, JSON success/error contracts, current pressed state, and CSRF-aware enhancement hooks |
| Hacker News service | Official endpoints, no credentials, normalization, URL fallback, deleted/dead/non-story/malformed filtering, rank preservation, 20–50 bounds, default 30, partial/total failures, timeout/network/status/JSON errors, empty results, and exact 60-second cache behaviour |
| External discovery UI | Public page and navigation, same-origin endpoint, controlled `503`, partial information, loading/busy/empty/error states, repeat-request prevention, user refresh, safe DOM creation, `textContent`, validated external links, and attribution |
| Error pages | Custom 400, 403, 404, and 500 handlers/templates, correct statuses, plain language, no exception disclosure, and working home links |
| Responsive/accessibility implementation | Comment hierarchy, vote pressed/busy/live states, discovery status announcements, flexible action groups, responsive external cards, error-page presentation, safe new-tab cues, and visible native controls |

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
| Pending comments | A public detail page had no comment visibility rules | Approved comments are public; only the author can also see their pending comments |
| Comment ownership | Comment edit/delete URLs did not exist | Owners can update/delete; other members receive `404` and cannot mutate content |
| Vote transition | A second vote violated the database uniqueness constraint | An opposite vote updates the record; repeating the same vote removes it |
| Invalid vote | Missing/non-allowlisted values raised conversion or database errors | Only `1` and `-1` are accepted and invalid input receives controlled `400` feedback |
| Enhanced voting | Successful votes always redirected | Same-origin requests receive score/state JSON while ordinary forms still redirect correctly |
| Top stories | The Hacker News client module did not exist | Official top-story and item endpoints are requested with a configured timeout and no credentials |
| External validation | Unsafe/missing URLs and malformed records passed into normalization | Unsafe links fall back to Hacker News and unusable records are excluded |
| Partial upstream failure | One failed item request discarded the feed | Valid ranked items remain available and the endpoint/UI identify the result as partial |
| Cache boundary | Every feed call would have repeated all upstream work | Completed normalized results use a stable key and an exact 60-second server cache |
| Discovery loading | The discovery page referenced no custom behaviour | The relevant container alone starts a same-origin request with busy, disabled, success, empty, error, and refresh states |
| Error handlers | Missing routes used Django's default response | Custom status-correct, navigable, plain-language pages handle 400/403/404/500 |

One early template assertion attempted structural HTML comparison on a partial snippet and was corrected to a literal content assertion. A message test also initially attached the wrong storage fixture and was corrected to render with a message instance. These were test-harness corrections, not application defect resolutions.

## Current Phase 3 automated result

The following commands were run from the repository root after the Phase 3 implementation was complete:

```text
python manage.py test
Ran 172 tests in 103.698s
OK

python manage.py check
System check identified no issues (0 silenced).

python manage.py makemigrations --check --dry-run
No changes detected

python manage.py migrate --plan
No planned migration operations.

node --check static/js/voting.js
node --check static/js/external-feed.js
Both commands exited successfully without syntax errors.
```

The duration is machine-specific. The meaningful result is that all 98 earlier tests remain present within the 172 passing tests, Django reported no system-check issue, JavaScript syntax checks passed, and the model state had neither an uncreated nor unapplied migration. Every upstream HTTP interaction in the automated suite is mocked; the test run never contacts Hacker News.

## Manual Phase 3 browser checks

On 5 September 2026, the available browser-control capability was initialized for the required Phase 3 local UI pass. Browser discovery returned an empty list after the prescribed connection check, matching the Phase 2 limitation. No browser session existed to receive a local page, so no interactive viewport, keyboard, console, or network inspection could be performed and no manual pass is claimed.

The unexecuted scope includes comment create/edit/delete journeys, vote create/change/remove states, anonymous voting, discovery loading/success/failure/refresh, custom errors, narrow and wide responsive states, keyboard focus, live announcements, external links, horizontal overflow, console errors, and failed network requests. This also does not replace the formal Phase 4 matrix across supported browsers, screen readers, validators, contrast tools, zoom levels, performance tooling, or a deployed environment.

## Later testing

Phase 4 will execute and record the manual functional matrix, browser compatibility, keyboard-only journeys, screen-reader spot checks, contrast, zoom and reflow, HTML/CSS validation, deployment configuration, production migrations, static assets, and development/production parity. Results will be stated only after each check has run.
